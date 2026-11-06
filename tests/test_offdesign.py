"""Phase 2: evidence, path dependence, bounded continuation and partial maps."""
import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from scripts.run_throughflow import build_case
from sm_core import make_env
from sm_throughflow.offdesign import EnvironmentEvaluator, find_upper_boundary, trace_map
from sm_throughflow.outcomes import PointOutcome, failure_evidence
from sm_throughflow.solver import Annulus, InletCondition, QuasiNormals, Throughflow, ChokedError
from sm_throughflow.solver.errors import SolverError, PhysicalStateError
from sm_throughflow.solver.limits import inlet_capacity, solution_limits
from validation.run import model_anchors


def point(m, ok=True, kind="numerical_failure", value=1.2):
    return PointOutcome(m, ok, "converged" if ok else kind,
                        {"pressure_ratio_total": value} if ok else {}, restart={"m": m} if ok else None)


@pytest.mark.parametrize("error,classification,physical", [
    (ChokedError("iteration capacity"), "unresolved_capacity_limit", False),
    (SolverError("budget"), "numerical_failure", False),
    (PhysicalStateError("negative pressure"), "invalid_state", False),
    (SolverError("temperature", kind="outside_model_scope"), "unsupported_condition", False),
    (SolverError("sonic bound", kind="physical_capacity_exceeded"), "physical_limit", True),
    (ValueError("unanticipated bug"), "unexpected_error", False),
])
def test_failure_classification_does_not_promote_iteration_errors(error, classification, physical):
    evidence = failure_evidence(error)
    assert evidence["classification"] == classification
    assert evidence["physical_limit_established"] == physical
    json.dumps(evidence, allow_nan=False)


def test_analytic_sonic_bound_rejects_impossible_flow_before_iteration():
    annulus = Annulus.from_points([(0, .25), (.5, .25)], [(0, .35), (.5, .35)])
    flow = Throughflow(annulus, QuasiNormals.on(annulus, [0, .25, .5]),
                       InletCondition(101325., 288.15, alpha_deg=0.), mass_flow=20.)
    g = flow.gas
    # Independent density * sound speed at T*=2*T0/(gamma+1).
    ts = 288.15 * 2 / (g.gamma + 1)
    ps = 101325. * (ts / 288.15) ** (g.gamma / (g.gamma - 1))
    expected = np.pi * (.35**2 - .25**2) * ps / (g.R * ts) * np.sqrt(g.gamma * g.R * ts)
    assert inlet_capacity(flow)["capacity_kg_s"] == pytest.approx(expected, rel=1e-13)
    flow.mass_flow = expected * 1.01
    with pytest.raises(SolverError) as caught:
        flow.solve()
    assert failure_evidence(caught.value)["classification"] == "physical_limit"
    assert flow._effort["outer_iterations"] == 0
    flow.mass_flow = expected * .95
    assert flow.solve().convergence.converged


def test_uniform_duct_boundary_brackets_the_analytic_choke_flow():
    annulus = Annulus.from_points([(0, .25), (.5, .25)], [(0, .35), (.5, .35)])
    flow = Throughflow(annulus, QuasiNormals.on(annulus, [0, .25, .5]),
                       InletCondition(101325., 288.15, alpha_deg=0.), mass_flow=20.)
    capacity = inlet_capacity(flow)["capacity_kg_s"]
    def evaluate(m, seed):
        flow.mass_flow = m
        try:
            solution = flow.solve()
            return point(m, solution.convergence.converged)
        except SolverError as exc:
            d = failure_evidence(exc)
            return PointOutcome(m, False, d["classification"], diagnostics=d)
    boundary = find_upper_boundary(evaluate, capacity * .95, tolerance=1e-4)
    assert boundary["physical_choke_established"]
    assert boundary["lower_flow"] <= capacity < boundary["upper_flow"]
    assert boundary["model_choke_flow"] == pytest.approx(capacity, rel=1e-4)


def test_known_gas_scope_exclusion_precedes_a_capacity_claim():
    design, task = build_case(1)
    task["inlet"]["total_temperature_k"] = 500.
    evaluator = EnvironmentEvaluator(design, task)
    result = evaluator(500.)
    assert result.classification == "unsupported_condition"
    assert not result.diagnostics["physical_limit_established"]


def test_correlation_range_rejection_is_not_labelled_impossible_geometry():
    design, task = build_case(1)
    design["rows"][0]["blade_count"] = 4
    outcome = EnvironmentEvaluator(design, task)(80.)
    assert outcome.classification == "unsupported_condition"


def test_restart_rejects_unordered_and_nonfinite_surface_positions():
    annulus = Annulus.from_points([(0, .25), (.5, .25)], [(0, .35), (.5, .35)])
    flow = Throughflow(annulus, QuasiNormals.on(annulus, [0, .25, .5]),
                       InletCondition(101325., 288.15, alpha_deg=0.), mass_flow=20.)
    for state in (np.ones((3, 11)), np.full((3, 11), np.nan), np.zeros((2, 11))):
        with pytest.raises(SolverError, match="inadmissible restart"):
            flow.solve(start=state)


def test_stall_and_throat_indicators_are_not_choke_or_surge_proofs():
    sol = SimpleNamespace(rows=[SimpleNamespace(name="R")], performance={"R": SimpleNamespace(diagnostics={
        "equivalent_velocity_ratio": np.array([.5]), "stall_velocity_ratio": np.array([.6]),
        "throat_capacity_margin": np.array([-.02])})})
    limits = solution_limits(sol)
    assert limits["stall_criterion_crossed"] and limits["throat_capacity_exceeded"]
    assert not limits["physical_choke_established"] and not limits["surge_prediction"]


def test_adaptive_continuation_recovers_a_cold_hole_and_is_deterministic():
    def evaluate(m, seed):
        ok = m != 1.2 if seed is None else abs(m - seed["m"]) <= .061
        return point(m, ok)
    kwargs = dict(max_relative_step=.2, min_relative_step=.001)
    a = trace_map(evaluate, [1., 1.2, 1.4], **kwargs)
    assert a == trace_map(evaluate, [1., 1.2, 1.4], **kwargs)
    middle = a["points"][1]
    assert middle["converged"] and middle["initialization_sensitive"]
    assert not middle["paths"]["cold"]["converged"]
    assert middle["paths"]["ascending"]["converged"] and middle["paths"]["descending"]["converged"]
    assert any(p["intermediate"] for p in a["trace"])


def test_map_preserves_failed_interior_points_and_continues_after_them():
    result = trace_map(lambda m, seed: point(m, not 1.1 <= m <= 1.3), [1., 1.2, 1.4], max_bridge_attempts=3)
    assert [p["converged"] for p in result["points"]] == [True, False, True]
    assert result["interior_holes"] == [dict(mass_flow=1.2, lower_success=1., upper_success=1.4, classification="numerical_failure")]
    assert len(result["trace"]) < 20


def test_inconsistent_roots_are_reported_without_selecting_better_performance():
    def evaluate(m, seed):
        return point(m, value=1.2 if seed is None else 1.3 if seed["m"] < m else 1.1)
    result = trace_map(evaluate, [1., 1.02, 1.04])
    p = result["points"][1]
    assert p["classification"] == "path_sensitive" and p["metrics"] == {}
    assert p["path_differences"]["pressure_ratio_total"]["spread"] == pytest.approx(.2)


@pytest.mark.parametrize("kind,physical", [("numerical_failure", False), ("unresolved_capacity_limit", False), ("physical_limit", True)])
def test_boundary_requires_independent_physical_evidence(kind, physical):
    result = find_upper_boundary(lambda m, seed: point(m, m < 1.2, kind), 1., max_probes=50)
    assert result["lower_flow"] < 1.2 <= result["upper_flow"]
    assert result["bracket_resolved"]
    assert result["physical_choke_established"] == physical
    assert (result["model_choke_flow"] is not None) == physical


def test_boundary_is_bounded_when_every_point_succeeds_or_start_fails():
    a = find_upper_boundary(lambda m, seed: point(m), 1., max_probes=4)
    assert len(a["probes"]) == 4 and a["classification"] == "search_budget_exhausted"
    b = find_upper_boundary(lambda m, seed: point(m, False), 1.)
    assert len(b["probes"]) == 1 and b["classification"] == "no_converged_start"


def test_boundary_lookahead_does_not_mistake_an_isolated_hole_for_the_upper_limit():
    result = find_upper_boundary(lambda m, seed: point(m, m < 1.2 and not 1.019 < m < 1.021), 1.)
    assert result["lower_flow"] > 1.19
    assert any(not p["converged"] and p["mass_flow"] < result["lower_flow"] for p in result["probes"])


def test_anchors_never_interpolate_across_a_failed_gap():
    line = [dict(mass_flow=3., converged=True, stage_eta=.8, stage_pr=1.2, min_stall_margin=.1),
            dict(mass_flow=2., converged=False),
            dict(mass_flow=1., converged=True, stage_eta=.7, stage_pr=1.3, min_stall_margin=-.1)]
    peak, stall = model_anchors(line)
    assert peak["mass_flow"] == 3. and stall is None
    assert model_anchors([dict(converged=False, mass_flow=1.)]) == (None, None)


@pytest.fixture(scope="module")
def reference_evaluator():
    design, task = build_case(1)
    evaluator = EnvironmentEvaluator(design, task)
    return evaluator, evaluator(80.)


def test_real_neighbour_restart_agrees_with_cold_start_and_accounts_for_effort(reference_evaluator):
    evaluator, seed = reference_evaluator
    cold, warm = evaluator(78.), evaluator(78., seed.restart)
    assert cold.converged and warm.converged
    for key in ("pressure_ratio_total", "efficiency_isentropic", "power_W"):
        assert warm.metrics[key] == pytest.approx(cold.metrics[key], rel=1e-6)
    c = warm.diagnostics["convergence"]
    assert c["attempts"][0]["initialization"] == "restart"
    assert c["effort"]["outer_iterations"] == sum(a["effort"]["outer_iterations"] for a in c["attempts"])
    assert c["effort"]["station_solves"] > c["effort"]["outer_iterations"]


def test_restart_from_different_speed_is_not_used(reference_evaluator):
    evaluator, seed = reference_evaluator
    invalid = copy.deepcopy(seed.restart)
    invalid["key"] = "different-speed"
    outcome = evaluator(78., invalid)
    assert not outcome.converged and outcome.classification == "invalid_restart"


def test_failed_admissible_restart_retries_cold_and_retains_every_attempt(reference_evaluator, monkeypatch):
    evaluator, seed = reference_evaluator
    original = Throughflow._solve
    def reject_warm(self, tol, max_iterations, b_star, t_start=None, method="novak"):
        if t_start is not None:
            raise SolverError("forced warm-start nonconvergence", component="outer")
        return original(self, tol, max_iterations, b_star, t_start, method)
    monkeypatch.setattr(Throughflow, "_solve", reject_warm)
    outcome = evaluator(80., seed.restart)
    assert outcome.converged
    attempts = outcome.diagnostics["convergence"]["attempts"]
    assert [p["initialization"] for p in attempts] == ["restart", "restart", "cold"]
    assert [p["converged"] for p in attempts] == [False, False, True]
    assert outcome.metrics["pressure_ratio_total"] == seed.metrics["pressure_ratio_total"]


def test_partial_multipoint_result_keeps_successes_after_physical_failure():
    design, task = build_case(1)
    task["operating_points"] = [dict(name=str(m), mass_flow_kg_s=float(m), shaft_speed_rpm=5000.) for m in (80, 500, 78)]
    result = make_env("turbomachinery_throughflow").evaluate("partial", task, "one", design)
    assert result.status == "simulation_error" and result.metrics == {}
    points = result.raw_simulation_output["operating_points"]
    assert [p["converged"] for p in points] == [True, False, True]
    assert points[1]["failure"]["classification"] == "physical_limit"
    assert points[2]["metrics"]["pressure_ratio_total"] > 1.
    assert result.score.normalized_total == 0
    json.dumps(result.raw_simulation_output, allow_nan=False)


@pytest.mark.parametrize("all_failed", [False, True])
def test_validation_runner_retains_readings_and_never_flow_matches_a_numerical_boundary(tmp_path, monkeypatch, all_failed):
    import validation.run as runner
    design, _ = build_case(1)
    measured = [dict(reading=i, mass_flow=float(m), rpm=5000., stage_pr=1.2 + .01*i,
                     rotor_pr=1.25, stage_tr=1.1, rotor_tr=1.1, stage_eta=.85, rotor_eta=.9)
                for i, m in enumerate((80, 79, 78))]
    case = SimpleNamespace(STAGE_ETA_TR="rotor_tr", speeds=[100], design=design,
                           design_speed_rpm=5000., ASSUMPTIONS=[], notes=[], rotor_elements={}, stator_elements={},
                           inlet_blockage=lambda speed: .02, measured_points=lambda speed: measured)
    monkeypatch.setitem(runner.CASES, "fixture", lambda: case)
    monkeypatch.setattr(runner, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(runner, "REPORT", tmp_path / "report.md")
    def evaluate(design, m, rpm, blockage, restart=None):
        if all_failed or m == 79:
            return point(m, False, "numerical_failure")
        overall = {key: measured[0][key] for key in ("stage_pr", "rotor_pr", "stage_tr", "rotor_tr", "stage_eta", "rotor_eta")}
        return PointOutcome(m, True, "converged", overall, solution=SimpleNamespace(overall=overall, min_stall_margin=.1))
    monkeypatch.setattr(runner, "solve", evaluate)
    monkeypatch.setattr(runner, "choke_flow", lambda *args: dict(model_choke_flow=None, lower_flow=80., classification="numerical_failure_boundary"))
    line = [dict(mass_flow=80., converged=True, stage_eta=.85, stage_pr=1.2, min_stall_margin=.1)]
    monkeypatch.setattr(runner, "speed_line", lambda *args: (line, {}))
    result = runner.run_case("fixture")
    data = result["speeds"]["100"]
    assert len(data["readings"]) == 3
    assert all("at_matched_flow" not in p for p in data["readings"])
    assert data["readings"][1]["at_measured_flow"]["classification"] == "numerical_failure"
    if not all_failed:
        assert data["anchors"]["choke"]["model"] is None
        assert data["anchors"]["choke"]["error"] is None
    runner.report([result])
    assert (tmp_path / "report.md").exists()
