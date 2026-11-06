"""v7 refinement, equivalent roots and between-section admission."""
import numpy as np
import pytest

from scripts.run_throughflow import build_case
from sm_core import make_env
from sm_throughflow import ThroughflowDesignV2
from sm_throughflow.drc import run_drc
from sm_throughflow.geometry import GEOMETRY_SPANS, blade_sections
from sm_throughflow.solver.reposition import CoupledRepositioning


@pytest.mark.parametrize("subdivisions", [4, 8, 16])
def test_refined_axial_grids_converge_without_relaxing_tolerances(subdivisions):
    d, t = build_case(1)
    t["numerics"].update(duct_subdivisions=subdivisions)
    result = make_env("turbomachinery_throughflow").evaluate("refinement", t, "one", d)
    assert result.status == "success", result.error_message
    raw = result.raw_simulation_output["operating_points"][0]
    conv = raw["convergence"]
    assert conv["position_change"] <= 1e-7 and conv["velocity_change"] <= 1e-7
    assert conv["repositioning"]["method"] == "anderson"
    assert conv["repositioning"]["accepted_steps"] > 0
    assert conv["iterations"] < 400
    assert len(conv["attempts"]) == 1
    assert raw["verification"]["mass_relative_error"] < 1e-9
    assert raw["verification"]["energy_relative_error"] < 1e-10


def test_accelerated_and_original_iteration_find_the_same_coarse_root():
    d, t = build_case(1)
    t["numerics"]["tolerance"] = 1e-8
    env = make_env("turbomachinery_throughflow")
    accelerated = env.evaluate("a", t, "one", d)
    t["numerics"]["repositioning"] = "novak"
    original = env.evaluate("n", t, "one", d)
    assert accelerated.status == original.status == "success"
    for key in ("pressure_ratio_total", "efficiency_isentropic", "power_W", "exit_blockage"):
        assert accelerated.metrics[key] == pytest.approx(original.metrics[key], rel=2e-7)


def test_rejected_acceleration_restarts_history_and_keeps_ordered_surfaces():
    step = CoupledRepositioning()
    t = np.array([[0., .2, .6, 1.], [0., .3, .7, 1.]])
    # Repeated, almost dependent history creates an excessive extrapolation.
    x = np.r_[t.ravel(), [1., 1.]]
    f = np.r_[np.tile([0., .001, .001, 0.], 2), [0., 0.]]
    step.history = [(x - 1, f * (1 + 1e-7), f * (1 + 1e-7)),
                    (x - 2, f * (1 + 2e-7), f * (1 + 2e-7))]
    target = t + f[:t.size].reshape(t.shape)
    new, kb = step.step(t, target, np.ones_like(t), np.ones(2), np.ones(2), .5, .5)
    assert step.rejected == 1 and len(step.history) == 1
    assert np.array_equal(new, target) and np.array_equal(kb, np.ones(2))


def test_intermediate_projected_chord_can_violate_a_limit_despite_valid_nodes():
    design, _ = build_case(1)
    row = design["rows"][1]
    row["camberline"] = "circular_arc"
    row["metal_angle_in_deg"] = [-16.] * 5 + [24.] * 6
    row["metal_angle_out_deg"] = [a - 8 for a in row["metal_angle_in_deg"]]
    row["trailing_edge_axial_m"] = row["leading_edge_axial_m"] + .05 / 1.55
    model = ThroughflowDesignV2.model_validate(design)
    nodes = blade_sections(model.rows[1], model.passage.stations)
    assert all(.5 <= 1.55 * np.cos(np.radians(s["stagger"])) <= 1.5 for s in nodes)
    dense = blade_sections(model.rows[1], model.passage.stations, GEOMETRY_SPANS)
    assert max(1.55 * np.cos(np.radians(s["stagger"])) for s in dense) > 1.5
    ok, error = run_drc(model)
    assert not ok and "axial chord" in error


def test_repeated_spanwise_oscillations_are_explicitly_outside_scope():
    design, _ = build_case(1)
    design["rows"][0]["chord_m"] = [.05, .051, .05, .051, .05, .051, .05, .051, .05, .051, .05]
    ok, error = run_drc(ThroughflowDesignV2.model_validate(design))
    assert not ok and "unsupported spanwise oscillation" in error


def test_failed_accelerated_attempt_retries_original_method(monkeypatch):
    from sm_throughflow.solver.errors import SolverError
    def fail(*args, **kwargs):
        raise SolverError("forced accelerator failure", component="repositioning")
    monkeypatch.setattr(CoupledRepositioning, "step", fail)
    d, t = build_case(1)
    result = make_env("turbomachinery_throughflow").evaluate("fallback", t, "one", d)
    assert result.status == "success", result.error_message
    convergence = result.raw_simulation_output["operating_points"][0]["convergence"]
    assert convergence["repositioning"]["method"] == "novak"
    a, b = convergence["attempts"]
    assert a["method"] == "anderson" and not a["converged"]
    assert a["failure"]["component"] == "repositioning"
    assert b["method"] == "novak" and b["converged"]
    # v11 characterization retained: 1.1565119467130494. v12 resolves duct wall steps.
    assert result.metrics["pressure_ratio_total"] == pytest.approx(1.156503234988969, rel=1e-9)
