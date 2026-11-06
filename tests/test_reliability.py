"""Regressions for physical geometry, Reynolds coupling and success evidence."""
import copy
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from scripts.run_throughflow import build_case
from sm_core import make_env
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.drc import run_drc
from sm_throughflow.geometry import blade_sections
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.errors import SolverError, PhysicalStateError
from sm_throughflow.solver.verification import verify_solution

ROOT = Path(__file__).resolve().parents[1]


def evaluate(design, task):
    return make_env("turbomachinery_throughflow").evaluate("reliability", task, "design", design)


def build(design, task):
    d, t = ThroughflowDesignV2.model_validate(design), ThroughflowTaskV2.model_validate(task)
    flow, models = SlcAungierSimulator.build(d, t, t.operating_points[0])
    return flow, models


@pytest.fixture(scope="module")
def reference():
    d, t = build_case(1)
    result = evaluate(d, t)
    assert result.status == "success", result.error_message
    return d, t, result


def insert_contour(design, positions, contraction_at=None):
    modified = copy.deepcopy(design)
    points = modified["passage"]["stations"]
    old = copy.deepcopy(points)
    for x in positions:
        h, s = (float(np.interp(x, [p["axial_m"] for p in old], [p[key] for p in old]))
                for key in ("hub_radius_m", "shroud_radius_m"))
        points.append(dict(axial_m=x, hub_radius_m=h, shroud_radius_m=h + 0.02 if x == contraction_at else s))
    points.sort(key=lambda p: p["axial_m"])
    return modified


def test_hidden_inlet_constriction_cannot_pass_eighty_kg_per_second(reference):
    d, t, _ = reference
    modified = insert_contour(d, [0.02, 0.04, 0.06], contraction_at=0.04)
    assert run_drc(ThroughflowDesignV2.model_validate(modified))[0]
    flow, _ = build(modified, t)
    assert 0.04 in flow.qn.z_hub
    # Independently calculated ideal sonic capacity is less than 10 kg/s.
    area = np.pi * (flow.annulus.shroud_radius(.04) ** 2 - flow.annulus.hub_radius(.04) ** 2)
    gamma, R = flow.gas.gamma, flow.gas.R
    sonic_capacity = area * 101325 * np.sqrt(gamma / (R * 288.15)) * (2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1)))
    assert sonic_capacity < 10.0
    result = evaluate(modified, t)
    assert result.status == "simulation_error", result.metrics
    assert result.raw_simulation_output["failure"]["kind"] == "physical_capacity_exceeded"
    assert result.raw_simulation_output["failure"]["physical_limit_established"]


def test_collinear_points_do_not_change_the_discretization_or_result(reference):
    d, t, result = reference
    modified = insert_contour(d, [0.02, 0.04, 0.06, 0.10])
    again = evaluate(modified, t)
    assert again.status == "success", again.error_message
    assert again.metrics == result.metrics
    assert again.raw_simulation_output["operating_points"] == result.raw_simulation_output["operating_points"]


def test_unresolved_interior_annulus_throat_is_explicitly_rejected(reference):
    d, t, _ = reference
    row = d["rows"][0]
    a, b = row["leading_edge_axial_m"], row["trailing_edge_axial_m"]
    x = (a + b) / 2
    modified = insert_contour(d, [a, x, b], contraction_at=x)
    result = evaluate(modified, t)
    assert result.status == "drc_error"
    assert "unresolved interior annulus throat" in result.error_message
    with pytest.raises(ValueError, match="unresolved interior annulus throat"):
        build(modified, t)


def test_refinement_preserves_row_and_stage_mapping(reference):
    d, t, _ = reference
    t = copy.deepcopy(t)
    t["numerics"]["duct_subdivisions"] = 2
    flow, _ = build(d, t)
    for source, row in zip(d["rows"], flow.rows):
        assert flow.qn.z_hub[row.inlet] == source["leading_edge_axial_m"]
        assert flow.qn.z_hub[row.inlet + 1] == source["trailing_edge_axial_m"]
    result = evaluate(d, t)
    assert result.status == "success", result.error_message
    raw = result.raw_simulation_output["operating_points"][0]
    assert raw["row_station_indices"]["R1"]["inlet"] == 2
    assert raw["row_station_indices"]["S1"]["inlet"] == 5
    assert 1.1 < raw["stages"][0]["pressure_ratio_total"] < 1.3
    mixing = SlcAungierSimulator.spanwise_mixing(ThroughflowDesignV2.model_validate(d), flow.annulus, flow.rows[0].omega,
                                               {row.name: row.inlet for row in flow.rows})
    assert mixing.stage_in == 2 and mixing.stage_out == 6


def test_crossed_stage_labels_are_rejected():
    d, _ = build_case(2)
    d["rows"][1]["stage_id"] = "stage2"
    d["rows"][3]["stage_id"] = "stage1"
    with pytest.raises(ValidationError, match="preceding rotor"):
        ThroughflowDesignV2.model_validate(d)


def test_mca_drc_uses_constructed_stagger():
    from sm_throughflow.correlations.blade_geometry import mca_shape
    d, _ = build_case(1)
    r = d["rows"][0]
    r.update(profile="mca", camberline="multiple_circular_arc", edge_radius_to_chord=.004,
             thickness_to_chord=[.05] * 11, transition_point=[.55] * 11,
             turning_rate_ratio=[.4] * 11, max_thickness_location=[.6] * 11)
    model = ThroughflowDesignV2.model_validate(d)
    computed = blade_sections(model.rows[0], model.passage.stations)
    for k, section in enumerate(computed):
        theta = r["metal_angle_out_deg"][k] - r["metal_angle_in_deg"][k]
        chi1, _ = mca_shape(theta, .55, .4)
        assert section["stagger"] == pytest.approx(-r["metal_angle_in_deg"][k] - chi1)
    # Put the maximum projected chord exactly at the DRC upper boundary.
    axial_chords = np.array(r["chord_m"]) * np.cos(np.radians([s["stagger"] for s in computed]))
    r["trailing_edge_axial_m"] = r["leading_edge_axial_m"] + float(max(axial_chords)) / 1.499
    assert run_drc(ThroughflowDesignV2.model_validate(d))[0]


def test_reynolds_correction_changes_with_density_at_similar_operating_points(reference):
    d, t, high = reference
    low_task = copy.deepcopy(t)
    low_task["inlet"]["total_pressure_pa"] *= .5
    low_task["operating_points"][0]["mass_flow_kg_s"] *= .5
    low = evaluate(d, low_task)
    assert low.status == "success", low.error_message
    for high_row, low_row in zip(high.raw_simulation_output["operating_points"][0]["rows"],
                                 low.raw_simulation_output["operating_points"][0]["rows"]):
        assert np.all(np.asarray(high_row["reynolds_number"]) > 0)
        ratio = np.asarray(low_row["reynolds_number"]) / high_row["reynolds_number"]
        assert np.all((ratio > .45) & (ratio < .55))
        assert np.all(np.asarray(low_row["reynolds_loss_factor"]) > high_row["reynolds_loss_factor"])
    assert low.metrics["efficiency_isentropic"] < high.metrics["efficiency_isentropic"]


def test_success_carries_nested_convergence_and_balances(reference):
    raw = reference[2].raw_simulation_output
    point = raw["operating_points"][0]
    assert point["verification"]["mass_relative_error"] < 1e-9
    for entry in list(point["convergence"]["rows"].values()) + point["convergence"]["quasi_normals"] + point["convergence"]["endwalls"]:
        assert entry["residual"] <= entry["tolerance"]
        assert entry["iterations"] >= 1
    assert point["convergence"]["attempts"][-1]["loss_scale"] == 1.0
    for key in ("field_change", "blockage_change", "mixing_change", "position_change"):
        assert point["convergence"][key] <= point["convergence"]["tolerance"]
    assert raw["provenance"]["effective_inputs"]["physics_profile"]["viscosity_model"] == "sutherland_air"
    assert not point["validity"]["score_eligible"]
    json.dumps(raw, allow_nan=False)


@pytest.mark.parametrize("mode", ["temperature", "size"])
def test_reynolds_effect_at_similar_temperature_and_size(reference, mode):
    d, t = copy.deepcopy(reference[:2])
    if mode == "temperature":
        ratio = 1.1
        t["inlet"]["total_temperature_k"] *= ratio
        t["operating_points"][0]["mass_flow_kg_s"] /= np.sqrt(ratio)
        t["operating_points"][0]["shaft_speed_rpm"] *= np.sqrt(ratio)
        lower, upper = .84, .94
    else:
        for station in d["passage"]["stations"]:
            for key in station:
                station[key] *= 2.0
        for row in d["rows"]:
            for key in ("leading_edge_axial_m", "trailing_edge_axial_m", "tip_clearance_m", "hub_clearance_m"):
                if key in row:
                    row[key] *= 2.0
            row["chord_m"] = [2.0 * c for c in row["chord_m"]]
        t["operating_points"][0]["mass_flow_kg_s"] *= 4.0
        t["operating_points"][0]["shaft_speed_rpm"] /= 2.0
        lower, upper = 1.9, 2.1
    result = evaluate(d, t)
    assert result.status == "success", result.error_message
    for current, original in zip(result.raw_simulation_output["operating_points"][0]["rows"],
                                 reference[2].raw_simulation_output["operating_points"][0]["rows"]):
        ratio = np.asarray(current["reynolds_number"]) / original["reynolds_number"]
        assert np.all((ratio > lower) & (ratio < upper))


def test_constructed_adjacent_blades_cannot_intersect(reference):
    from sm_throughflow.geometry import validate_constructed_section
    model = ThroughflowDesignV2.model_validate(reference[0])
    row = model.rows[0]
    parameters = blade_sections(row, model.passage.stations)[0]
    parameters.update(stagger=80.0, solidity=3.0, t_c=.12)
    with pytest.raises(ValueError, match="adjacent constructed blades"):
        validate_constructed_section(row, parameters)


def test_optional_mixing_has_global_balance_checks(reference, monkeypatch):
    monkeypatch.setattr(SlcAungierSimulator, "mixing_model", "gallimore")
    coarse = evaluate(*reference[:2])
    # The coarse mixing solution satisfies the nonlinear stopping test but
    # violates the independent angular-momentum flux check. Do not loosen it.
    assert coarse.status == "simulation_error"
    failure = coarse.raw_simulation_output["failure"]
    assert failure["kind"] == "invalid_physical_state"
    assert "angular_momentum_flux" in failure["message"]
    assert failure["residual"] > failure["details"]["limit"]
    task = copy.deepcopy(reference[1])
    task["numerics"]["stream_surfaces"] = 41
    result = evaluate(reference[0], task)
    assert result.status == "success", result.error_message
    point = result.raw_simulation_output["operating_points"][0]
    checks = point["verification"]
    assert checks["energy_relative_error"] is None
    assert checks["integrated_energy_relative_error"] <= checks["limits"]["integrated_energy_relative_error"]
    assert checks["duct_angular_momentum_flux_relative_error"] <= checks["limits"]["duct_angular_momentum_flux_relative_error"]
    assert checks["min_stream_entropy_change_j_kg_k"] < 0.0  # allowed redistribution, not negative global production
    assert point["convergence"]["mixing_change"] <= point["convergence"]["tolerance"]
    assert result.raw_simulation_output["provenance"]["effective_inputs"]["mixing_model"] == "gallimore"


def test_unconverged_endwall_is_not_reported_as_success(reference, monkeypatch):
    from sm_throughflow.solver.endwall import EndwallBoundaryLayers
    original = EndwallBoundaryLayers.__init__

    def limited(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self.max_passes = 1

    monkeypatch.setattr(EndwallBoundaryLayers, "__init__", limited)
    d, t, _ = reference
    result = evaluate(d, t)
    assert result.status == "simulation_error"
    evidence = result.raw_simulation_output["failure"]
    assert evidence["component"] == "endwall" and evidence["iterations"] == 1
    assert evidence["residual"] > evidence["details"]["tolerance"]
    assert evidence["details"]["wall"] in ("hub", "shroud")
    json.dumps(result.raw_simulation_output, allow_nan=False)


@pytest.mark.parametrize("component", ["row", "quasi_normal", "outer"])
def test_each_required_iteration_limit_fails_explicitly(reference, monkeypatch, component):
    import sm_throughflow.solver.throughflow as module
    d, t = copy.deepcopy(reference[:2])
    if component == "row":
        original = module.Throughflow._row_station
        def limited(self, *args, **kwargs):
            kwargs["max_passes"] = 1
            return original(self, *args, **kwargs)
        monkeypatch.setattr(module.Throughflow, "_row_station", limited)
    elif component == "quasi_normal":
        original = module.solve_quasi_normal
        def limited(*args, **kwargs):
            kwargs["max_inner"] = 1
            return original(*args, **kwargs)
        monkeypatch.setattr(module, "solve_quasi_normal", limited)
    else:
        t["numerics"]["max_iterations"] = 10
    result = evaluate(d, t)
    assert result.status == "simulation_error"
    failure = result.raw_simulation_output["failure"]
    assert failure["component"] == component
    assert failure["iterations"] >= 1
    attempts = failure.get("attempts", failure.get("details", {}).get("attempts"))
    assert len(attempts) >= 2  # cold start and failed homotopy evidence retained
    json.dumps(result.raw_simulation_output, allow_nan=False)


def test_negative_row_loss_is_rejected(reference):
    from sm_throughflow.solver import PrescribedRow
    d, t, _ = reference
    flow, _ = build(d, t)
    row = flow.rows[0]
    flow.row_at[row.inlet] = replace(row, model=PrescribedRow(-40.0, loss=-.01))
    with pytest.raises(PhysicalStateError, match="nonnegative"):
        flow.solve()


def test_smoothing_cannot_hide_negative_row_loss(reference, monkeypatch):
    import sm_throughflow.solver.aungier_row as module
    monkeypatch.setattr(module, "smooth_loss", lambda dp: -np.abs(dp))
    result = evaluate(*reference[:2])
    assert result.status == "simulation_error"
    assert result.raw_simulation_output["failure"]["kind"] == "invalid_physical_state"
    assert "smoothing" in result.error_message


def test_converged_solution_with_corrupted_energy_is_rejected(reference):
    flow, _ = build(*reference[:2])
    solution = flow.solve(tol=1e-7, b_star=16.)
    corrupted = list(solution.stations)
    corrupted[2] = replace(corrupted[2], H=corrupted[2].H + 1000.0)
    with pytest.raises(PhysicalStateError, match="energy"):
        verify_solution(flow, replace(solution, stations=corrupted), 1e-7)
    corrupted = list(solution.stations)
    corrupted[-1] = replace(corrupted[-1], C_theta=corrupted[-1].C_theta + 1.0)
    with pytest.raises(PhysicalStateError, match="angular_momentum"):
        verify_solution(flow, replace(solution, stations=corrupted), 1e-7)


def test_old_version_and_custom_gas_are_not_silently_reinterpreted(reference):
    task = copy.deepcopy(reference[1])
    task["simulator_version"] = "slc_aungier_experimental_v5"
    with pytest.raises(ValidationError):
        ThroughflowTaskV2.model_validate(task)
    del task["simulator_version"]
    task["gas"] = {"cp_j_kg_k": 1200.0, "gas_constant_j_kg_k": 287.05}
    with pytest.raises(ValidationError, match="dry air"):
        ThroughflowTaskV2.model_validate(task)


def test_metrics_are_identical_in_an_independent_process(reference):
    payload = json.dumps({"design": reference[0], "task": reference[1]})
    script = "import json,sys; from sm_core import make_env; p=json.load(sys.stdin); r=make_env('turbomachinery_throughflow').evaluate('t',p['task'],'d',p['design']); assert r.status=='success',r.error_message; print(json.dumps(r.metrics))"
    result = subprocess.run([sys.executable, "-c", script], input=payload, text=True, capture_output=True, check=True, cwd=ROOT)
    assert json.loads(result.stdout) == reference[2].metrics


def test_campaign_results_are_exclusive_and_historical_run_requires_opt_in(tmp_path):
    sys.path.insert(0, str(ROOT / "validation"))
    from campaign import write_json_new
    import run
    path = tmp_path / "result.json"
    write_json_new(path, {"value": 1})
    with pytest.raises(FileExistsError):
        write_json_new(path, {"value": 2})
    assert json.loads(path.read_text()) == {"value": 1}
    with pytest.raises(ValueError, match="campaign"):
        run.run_case("nasa_stage35")


def test_changed_source_cannot_be_stamped_as_the_imported_solver(monkeypatch):
    from sm_throughflow import provenance
    monkeypatch.setattr(provenance, "_source_files", lambda: {"modified.py": "changed"})
    with pytest.raises(RuntimeError, match="source changed after import"):
        provenance.runtime_identity()


def test_multistage_endwall_budget_is_explicit_and_sufficient():
    design, task = build_case(3)
    short = copy.deepcopy(task)
    short["numerics"]["endwall_max_iterations"] = 10
    failed = evaluate(design, short)
    assert failed.status == "simulation_error"
    failure = failed.raw_simulation_output["failure"]
    assert failure["component"] == "endwall" and failure["iterations"] == 10
    result = evaluate(design, task)
    assert result.status == "success", result.error_message
    raw = result.raw_simulation_output
    assert raw["provenance"]["effective_inputs"]["task"]["numerics"]["endwall_max_iterations"] == 200
    point = raw["operating_points"][0]
    assert len(point["stages"]) == 3
    assert 1.5 < result.metrics["pressure_ratio_total"] < 1.7
    assert point["verification"]["energy_relative_error"] < 1e-10
    assert all(wall["residual"] <= wall["tolerance"] for wall in point["convergence"]["endwalls"])
