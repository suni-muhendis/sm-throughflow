"""Independent checks on experimental adapters and conservative qualification."""
from copy import deepcopy
import json

import numpy as np
import pytest

from scripts.run_throughflow import build_case
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.gas import PerfectGas
from sm_throughflow.solver.rows import ExitGeometry
from validation.phase3 import (PROTOCOL_PATH, projected_geometry, gap_variant, interpolate_observation,
                               statistics, empirical_gate, plain, task_for, V)
from validation.phase3_rows import row_model, station, reconstructed_loss, extend, measured_states, geometry_file, condition_result
from validation.phase3_report import quadrature_weights, normalized_shape, row_statistics, compare_family_delta


def test_projection_preserves_blade_edges_duct_vertices_and_original():
    design, _ = build_case(1)
    row = design["rows"][0]
    x1, x2 = row["leading_edge_axial_m"], row["trailing_edge_axial_m"]
    for x, hub in ((.04, .31), (x1, .312), ((x1+x2)/2, .32), (x2, .314)):
        design["passage"]["stations"].append(dict(axial_m=x, hub_radius_m=hub, shroud_radius_m=.49))
    design["passage"]["stations"].sort(key=lambda s: s["axial_m"])
    original = deepcopy(design)
    projected, evidence = projected_geometry(design)
    assert design == original
    nodes = {s["axial_m"]: s for s in projected["passage"]["stations"]}
    for old in original["passage"]["stations"]:
        if old["axial_m"] in (.04, x1, x2):
            assert nodes[old["axial_m"]] == old
    assert (x1+x2)/2 not in nodes
    assert evidence["max_wall_displacement_m"] == pytest.approx(.007)
    assert evidence["max_relative_annulus_area_change"] > 0
    assert not evidence["release_evidence"]


def test_gap_changes_gap_without_changing_row_widths_or_radii():
    design, _ = build_case(1)
    changed = gap_variant(design, 1.5)
    first, second = changed["rows"]
    oldgap = design["rows"][1]["leading_edge_axial_m"] - first["trailing_edge_axial_m"]
    assert second["leading_edge_axial_m"] - first["trailing_edge_axial_m"] == pytest.approx(oldgap*1.5)
    for a, b in zip(design["rows"], changed["rows"]):
        assert a["trailing_edge_axial_m"]-a["leading_edge_axial_m"] == pytest.approx(b["trailing_edge_axial_m"]-b["leading_edge_axial_m"])


def test_interpolation_is_inside_overlap_only_and_preserves_units():
    points = [dict(reading="a", mass_flow=2., stage_pr=1.2, stage_eta=.8), dict(reading="b", mass_flow=4., stage_pr=1.4, stage_eta=.9)]
    mid = interpolate_observation(points, 3.)
    assert mid["stage_pr"] == pytest.approx(1.3)
    assert mid["stage_eta"] == pytest.approx(.85)
    with pytest.raises(ValueError, match="no extrapolation"):
        interpolate_observation(points, 4.1)
    with pytest.raises(ValueError):
        interpolate_observation([points[0], points[0]], 2.)


def test_missing_error_samples_and_singletons_cannot_pass():
    limits = dict(absolute_bias=.05, sample_spread=.02, absolute_p90=.1)
    assert statistics([.01, .01], limits)["passed"]
    assert not statistics([.01], limits)["passed"]
    assert not statistics([], limits)["passed"]
    assert not statistics([.01, None, .01], limits)["passed"]
    assert statistics([.2, .2], limits)["sample_spread"] == 0
    assert not statistics([.2, .2], limits)["passed"]
    assert plain(dict(a=np.nan, b=np.bool_(True))) == dict(a=None, b=True)


def test_no_holdout_or_bad_admission_can_open_empirical_gate():
    threshold = json.loads(PROTOCOL_PATH.read_text())["screening_thresholds"]
    kwargs = dict(admission_passed=True, coverage=1., error_passed=True, profiles_passed=True, response_passed=True,
                  uncertainty_resolved=True, holdout_families=2, thresholds=threshold)
    assert empirical_gate(**kwargs)["qualified"]
    for key, value in (("admission_passed", False), ("holdout_families", 0), ("coverage", .94), ("profiles_passed", False)):
        assert not empirical_gate(**(kwargs | {key: value}))["qualified"]


def test_preregistered_numerics_reach_effective_task():
    protocol = json.loads(PROTOCOL_PATH.read_text())
    task = ThroughflowTaskV2.model_validate(task_for(dict(mass_flow=20., rpm=17000.), .02, protocol))
    for key, value in protocol["numerics"].items():
        assert getattr(task.numerics, key) == value


def test_extrapolation_labels_and_retains_observations():
    assert extend([.1, .9], [1., 3.], [0., 1.]) == pytest.approx([1., 1., 3., 3.])
    assert extend([.1, .9], [1., 3.], [0., 1.], "linear") == pytest.approx([.75, 1., 3., 3.25])
    with pytest.raises(ValueError):
        extend([.1, .9], [1., 3.], [.2, 1.])


def test_station_units_energy_and_isentropic_rotor_loss_basis():
    gas = PerfectGas()
    r = np.linspace(.3, .5, 11)
    z, wm, ct = np.zeros(11), np.full(11, 150.), np.zeros(11)
    t0, p0 = np.full(11, 288.15), np.full(11, 101325.)
    inlet = station(r, z, wm, ct, t0, p0, 500., 80., gas)
    r2, ct2 = r*.98, np.full(11, 60.)
    H2 = inlet.H + inlet.omega*(r2*ct2-r*ct)
    exit = station(r2, z+.06, wm, ct2, H2/gas.cp, gas.pressure(H2, inlet.s), 500., 80., gas)
    assert exit.I == pytest.approx(inlet.I)
    assert reconstructed_loss(inlet, exit, gas) == pytest.approx(np.zeros(11), abs=1e-13)
    lossy = station(r2, z+.06, wm, ct2, H2/gas.cp, gas.pressure(H2, inlet.s)*.98, 500., 80., gas)
    assert np.all(reconstructed_loss(inlet, lossy, gas) > 0)


@pytest.mark.parametrize("index", [0, 1])
def test_isolated_factory_matches_production_assembly(index):
    design, task = build_case(1)
    task = ThroughflowTaskV2.model_validate(task)
    flow, models = SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(design), task, task.operating_points[0])
    row = design["rows"][index]
    production = models[row["row_id"]]
    isolated = row_model(design, index, task.operating_points[0].shaft_speed_rpm, flow.gas)
    r = np.linspace(.31, .49, 11)
    z = np.full(11, row["leading_edge_axial_m"])
    inlet = station(r, z, np.full(11, 150.), np.full(11, 0. if index == 0 else 60.),
                    np.full(11, 300.), np.full(11, 110000.), production.omega, 80., flow.gas)
    exit = station(r, np.full(11, row["trailing_edge_axial_m"]), inlet.Wm, np.full(11, 60. if index == 0 else 0.),
                   np.full(11, 310.), np.full(11, 120000.), production.omega, 80., flow.gas)
    eg = ExitGeometry(exit.t, exit.y, exit.r, exit.z)
    a, b = production(inlet, exit, eg), isolated(inlet, exit, eg)
    assert np.array_equal(a.loss, b.loss)
    assert np.array_equal(a.exit_angle, b.exit_angle)
    assert plain(a.diagnostics) == plain(b.diagnostics)


def test_measured_state_adapter_has_correct_units_sign_and_unmodified_samples():
    case = V.CASES["nasa_stage35"]()
    p = next(p for p in case.measured_points(100) if p["reading"] == "3978")
    elements = case.rotor_elements[p["reading"]]
    geometry = V.L.read_geometry(geometry_file(case.case_id, 0))
    inlet, exit, rows = measured_states(elements, geometry, p["rpm"], p["mass_flow"])
    i = next(i+1 for i, r in enumerate(rows) if r["RP"] == 1)
    assert inlet.r[i] == pytest.approx(.24915)
    assert inlet.P0[i] == pytest.approx(99100.)
    assert inlet.T0[i] == pytest.approx(288.8)
    assert exit.P0[i]/inlet.P0[i] == pytest.approx(1.819)
    assert exit.T0[i]/inlet.T0[i] == pytest.approx(1.233)
    assert np.degrees(inlet.beta[i]) == pytest.approx(-67.2, abs=.2)
    assert inlet.C_theta[i] == -.4
    assert exit.C_theta[i] == 156.3
    assert inlet.r[0] < inlet.r[1] < inlet.r[-2] < inlet.r[-1]


def test_missing_derived_cells_do_not_discard_available_measured_states():
    case = V.CASES["nasa_stage37"]()
    p = next(p for p in case.measured_points(100) if p["reading"] == "4188")
    result = condition_result(case, 100, p, 1)
    hub_probe = next(p for p in result["points"] if p["span_from_tip"] == 95)
    assert hub_probe["span_inferred_from_radial_position"]
    assert hub_probe["deviation_error"] is None
    assert hub_probe["loss_error"] is None
    assert np.isfinite(hub_probe["relative_exit_angle_error_deg"])
    assert len(result["points"]) == 9


def test_profile_quadrature_uses_density_radius_and_radial_spacing():
    weight = quadrature_weights([1., 2., 4.], [1., 2., 3.], [2., 2., 1.])
    assert weight == pytest.approx(np.array([1., 12., 12.])/25.)
    assert normalized_shape([11., 11., 11.], 1., weight) == pytest.approx(np.zeros(3))
    assert np.dot(weight, normalized_shape([2., 3., 4.], 1., weight)) == pytest.approx(0., abs=1e-15)
    with pytest.raises(ValueError):
        normalized_shape([1., 1., 1.], 1., weight)


def test_grouping_does_not_count_radial_probes_as_independent_readings():
    point = dict(core=True, mach=.7, reynolds=6e5, loading=.3, deviation_error=.1, loss_error=.01,
                 conditional_work_error_relative=.01, downstream_angle_error_deg=.1)
    row = dict(case="one_machine", reading="one_reading", row_type="rotor", machine_family="one_family",
               blade_family="circular_arc", damper_presence="absent", speed=100, points=[point]*9)
    groups = row_statistics([row], json.loads(PROTOCOL_PATH.read_text()))
    assert all(g["readings"] == 1 for g in groups.values())
    assert all(not g["sufficient_development_support"] for g in groups.values())
    assert all(not g["diagnostic_deviation_loss_screen_passed"] for g in groups.values())


def test_family_delta_screens_keep_sign_and_percentage_point_units():
    threshold = json.loads(PROTOCOL_PATH.read_text())["screening_thresholds"]
    result = compare_family_delta(dict(stage_pr=-.025, stage_eta=-.024), dict(stage_pr=.014, stage_eta=.0025), threshold)
    assert result["efficiency_delta_error_points"] == pytest.approx(2.65)
    assert not result["efficiency_delta_passed"] and not result["pressure_delta_passed"]
    assert set(result["nominal_direction"].values()) == {"reversed_or_flat_sign"}
    assert not compare_family_delta(dict(stage_pr=.02, stage_eta=.01), None, threshold)["pressure_delta_passed"]
