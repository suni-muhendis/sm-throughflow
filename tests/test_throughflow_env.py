"""Contracts, design-rule check and simulator through the environment."""
import copy

import pytest
from pydantic import ValidationError

from sm_core import make_env
from scripts.run_throughflow import build_case
from sm_throughflow import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.drc import run_drc
from sm_throughflow.score import ExperimentalThroughflowScore
from sm_throughflow.simulator import SlcAungierSimulator


@pytest.fixture(scope="module")
def one_stage():
    design, task = build_case(1)
    task["operating_points"].append({"name": "part_speed", "mass_flow_kg_s": 72.0, "shaft_speed_rpm": 4500.0})
    result = make_env("turbomachinery_throughflow").evaluate("t", task, "d", design)
    return design, task, result


def _row(design, row_id):
    return next(r for r in design["rows"] if r["row_id"] == row_id)


# ------------------------------------------------------------------ contracts
def test_reference_cases_validate():
    for stages in (1, 3, 8):
        design, task = build_case(stages)
        assert ThroughflowDesignV2.model_validate(design).stage_count == stages
        ThroughflowTaskV2.model_validate(task)
    design, _ = build_case(2, inlet_guide_vane=True)
    assert ThroughflowDesignV2.model_validate(design).inlet_guide_vanes() == ["IGV"]


def test_rotor_needs_a_tip_clearance_and_a_stator_one_hub_treatment():
    design, _ = build_case(1)
    del _row(design, "R1")["tip_clearance_m"]
    with pytest.raises(ValidationError, match="tip_clearance_m"):
        ThroughflowDesignV2.model_validate(design)
    design, _ = build_case(1)
    _row(design, "S1")["shroud_seal"] = {"clearance_m": 3e-4, "fin_count": 3, "fin_pitch_m": 0.006, "fin_thickness_m": 3e-4}
    with pytest.raises(ValidationError, match="exactly one"):
        ThroughflowDesignV2.model_validate(design)


def test_sections_must_turn_the_same_way_and_rows_must_not_overlap():
    design, _ = build_case(1)
    _row(design, "S1")["metal_angle_out_deg"][5] = 80.0
    with pytest.raises(ValidationError, match="same way"):
        ThroughflowDesignV2.model_validate(design)
    design, _ = build_case(1)
    _row(design, "S1")["leading_edge_axial_m"] = _row(design, "R1")["trailing_edge_axial_m"]
    with pytest.raises(ValidationError, match="ordered"):
        ThroughflowDesignV2.model_validate(design)


def test_extra_fields_are_rejected():
    design, task = build_case(1)
    design["rows"][0]["loss_model"] = "anything"  # the referee is not the design's to choose
    with pytest.raises(ValidationError):
        ThroughflowDesignV2.model_validate(design)
    task["physics"] = {"physics_profile": "axial_compressor_aungier_v2", "K1": 0.001}
    with pytest.raises(ValidationError):
        ThroughflowTaskV2.model_validate(task)


def test_double_circular_arc_rows_carry_their_edge_radius():
    design, _ = build_case(1)
    rotor = _row(design, "R1")
    rotor["profile"], rotor["camberline"] = "dca", "circular_arc"
    with pytest.raises(ValidationError, match="edge_radius_to_chord"):
        ThroughflowDesignV2.model_validate(design)
    rotor["edge_radius_to_chord"] = 0.005
    ThroughflowDesignV2.model_validate(design)
    design, _ = build_case(1)
    _row(design, "R1")["edge_radius_to_chord"] = 0.005
    with pytest.raises(ValidationError, match="edge_radius_to_chord"):
        ThroughflowDesignV2.model_validate(design)


def _mca(row):
    row.update(profile="mca", camberline="multiple_circular_arc", edge_radius_to_chord=0.004, thickness_to_chord=[0.05] * 11,
               transition_point=[0.55] * 11, turning_rate_ratio=[0.4] * 11, max_thickness_location=[0.6] * 11)


def test_multiple_circular_arc_rows_carry_their_shape():
    design, _ = build_case(1)
    rotor = _row(design, "R1")
    _mca(rotor)
    ThroughflowDesignV2.model_validate(design)
    del rotor["turning_rate_ratio"]
    with pytest.raises(ValidationError, match="turning_rate_ratio"):
        ThroughflowDesignV2.model_validate(design)
    _mca(rotor)
    rotor["camberline"] = "circular_arc"
    with pytest.raises(ValidationError, match="go together"):
        ThroughflowDesignV2.model_validate(design)
    design, _ = build_case(1)
    _row(design, "R1")["transition_point"] = [0.5] * 11
    with pytest.raises(ValidationError, match="multiple_circular_arc"):
        ThroughflowDesignV2.model_validate(design)


# ------------------------------------------------------------------ design rules
def _drc(design):
    return run_drc(ThroughflowDesignV2.model_validate(design))


def test_reference_case_passes_the_design_rules():
    assert _drc(build_case(3)[0]) == (True, None)


@pytest.mark.parametrize("change, message", [
    (lambda r: r.update(thickness_to_chord=[0.15] * 11), "thickness_to_chord"),
    (lambda r: r.update(blade_count=4), "solidity"),
    (lambda r: r.update(trailing_edge_axial_m=r["leading_edge_axial_m"] + 0.012), "axial chord"),
    (lambda r: r.update(tip_clearance_m=0.02), "clearance"),
])
def test_design_rules_reject_geometry_outside_the_correlations(change, message):
    design, _ = build_case(1)
    change(_row(design, "R1"))
    ok, error = _drc(design)
    assert not ok and message in error


def test_seal_clearance_is_limited_by_eglis_model():
    design, _ = build_case(1)
    stator = _row(design, "S1")
    del stator["hub_clearance_m"]
    stator["shroud_seal"] = {"clearance_m": 2e-3, "fin_count": 3, "fin_pitch_m": 0.006, "fin_thickness_m": 3e-4}
    ok, error = _drc(design)
    assert not ok and "Egli" in error


# ------------------------------------------------------------------ evaluation
def test_task_runs_and_is_stamped(one_stage):
    _, _, result = one_stage
    assert result.status == "success", result.error_message
    assert result.simulator_version == SlcAungierSimulator.VERSION
    assert result.score_version == ExperimentalThroughflowScore.VERSION
    assert result.score.normalized_total == 0.0
    m = result.metrics
    assert 1.1 < m["pressure_ratio_total"] < 1.4
    assert 0.85 < m["efficiency_polytropic"] < 0.95
    assert m["efficiency_isentropic"] < m["efficiency_polytropic"]
    assert m["stream_surface_count"] == 11 and m["stage_count"] == 1
    # The short one-stage passage contracts by about 12%, so the accelerating exit flow
    # thins the end-wall layers below their inlet value; they still block the flow.
    assert 0.0 < m["exit_blockage"] < 0.1 and m["max_blockage"] >= 0.02


def test_every_operating_point_is_reported(one_stage):
    _, _, result = one_stage
    m = result.metrics
    assert "part_speed.pressure_ratio_total" in m
    assert m["part_speed.pressure_ratio_total"] < m["pressure_ratio_total"]


def test_evaluation_is_deterministic(one_stage):
    design, task, result = one_stage
    again = make_env("turbomachinery_throughflow").evaluate("t", copy.deepcopy(task), "d", copy.deepcopy(design))
    assert again.metrics == result.metrics


def test_throats_come_from_the_constructed_blades(one_stage):
    _, _, result = one_stage
    for row in result.raw_simulation_output["operating_points"][0]["rows"]:
        throats = row["section_throat_over_pitch"]
        assert len(throats) == 11 and all(0.2 < t < 1.0 for t in throats)


def test_double_circular_arc_rotor_runs():
    design, task = build_case(1)
    rotor = _row(design, "R1")
    rotor.update(profile="dca", camberline="circular_arc", edge_radius_to_chord=0.005, thickness_to_chord=[0.05] * 11)
    result = make_env("turbomachinery_throughflow").evaluate("t", task, "d", design)
    assert result.status == "success", result.error_message


def test_multiple_circular_arc_rotor_runs():
    design, task = build_case(1)
    _mca(_row(design, "R1"))
    result = make_env("turbomachinery_throughflow").evaluate("t", task, "d", design)
    assert result.status == "success", result.error_message


def test_shrouded_stators_and_inlet_guide_vanes_run():
    design, task = build_case(1, inlet_guide_vane=True)
    stator = _row(design, "S1")
    del stator["hub_clearance_m"]
    stator["shroud_seal"] = {"clearance_m": 3e-4, "fin_count": 3, "fin_pitch_m": 0.006, "fin_thickness_m": 3e-4}
    result = make_env("turbomachinery_throughflow").evaluate("t", task, "d", design)
    assert result.status == "success", result.error_message
    rows = {r["row_id"]: r for r in result.raw_simulation_output["operating_points"][0]["rows"]}
    assert rows["S1"]["seal_leakage_mass_flow"] > 0.0  # from the stator exit back to its inlet
    assert max(rows["S1"]["seal_loss"]) > 0.0


# Characterization goldens of the simulator (slc_aungier_experimental_v5) on the one-stage reference case. A change
# here moves a number: it needs a new simulator version, not new goldens.
GOLDEN_V5 = {
    "pressure_ratio_total": 1.1559528688496092,
    "efficiency_polytropic": 0.9262041947750057,
    "power_W": 1058884.127132292,
    "exit_blockage": 0.01811810156598237,
    "min_stall_margin": 0.11735803721536975,
    "max_loss_coefficient": 0.034157785795312284,
    "part_speed.pressure_ratio_total": 1.1525286524165972,
    "part_speed.efficiency_polytropic": 0.9215524976990491,
}


# New characterization after the v6 geometry/Reynolds and convergence changes.
# GOLDEN_V5 above is retained unchanged as historical evidence.
GOLDEN_V6 = {
    "pressure_ratio_total": 1.1567192537471698,
    "efficiency_polytropic": 0.9298351613408458,
    "power_W": 1059588.323923194,
    "exit_blockage": 0.018153459326727406,
    "min_stall_margin": 0.11674036207385319,
    "max_loss_coefficient": 0.0327548779106237,
    "part_speed.pressure_ratio_total": 1.1532624785455987,
    "part_speed.efficiency_polytropic": 0.9252480414920448,
}


GOLDEN_V7 = {
    "pressure_ratio_total": 1.156719254239527,
    "efficiency_polytropic": 0.9298351614871739,
    "power_W": 1059588.3269203913,
    "exit_blockage": 0.01815345932104917,
    "min_stall_margin": 0.11674036877462424,
    "max_loss_coefficient": 0.03275487756004808,
    "part_speed.pressure_ratio_total": 1.1532624779259137,
    "part_speed.efficiency_polytropic": 0.9252480417732972,
}


# Cold-start equations are unchanged by the v8 map/restart policy.
GOLDEN_V8 = dict(GOLDEN_V7)


# v9 integrates radial momentum in squared velocity and retains interior wall controls.
GOLDEN_V9 = {
    'pressure_ratio_total': 1.1567172120705462,
    'efficiency_polytropic': 0.9298425104689564,
    'power_W': 1059566.6250551753,
    'exit_blockage': 0.018149846346298792,
    'min_stall_margin': 0.11622013560170008,
    'max_loss_coefficient': 0.0327604141412902,
    'part_speed.pressure_ratio_total': 1.153259205979998,
    'part_speed.efficiency_polytropic': 0.9252438813583737,
}


# v10 wall-layer integration and safeguarded coupled iteration.
GOLDEN_V10 = {
    'pressure_ratio_total': 1.1568402682985828,
    'efficiency_polytropic': 0.9298352971481215,
    'power_W': 1060366.7142778968,
    'exit_blockage': 0.017865670901901387,
    'min_stall_margin': 0.11559705333074666,
    'max_loss_coefficient': 0.0328127840410134,
    'part_speed.pressure_ratio_total': 1.1533464698272964,
    'part_speed.efficiency_polytropic': 0.925227993819821,
}


# v11 direct curvature and stencil-compatible damping.
GOLDEN_V11 = {'pressure_ratio_total': 1.1565119507650088, 'efficiency_polytropic': 0.9292737811472033, 'power_W': 1058908.2043074714, 'exit_blockage': 0.017865582071399655, 'min_stall_margin': 0.12137456542578762, 'max_loss_coefficient': 0.033023458906974945, 'part_speed.pressure_ratio_total': 1.153026318765347, 'part_speed.efficiency_polytropic': 0.9252726157312785}


GOLDEN_V12 = {'pressure_ratio_total': 1.1565032390316168, 'efficiency_polytropic': 0.9292733294616159,
              'power_W': 1058852.6390022554, 'exit_blockage': 0.017909803983055195,
              'min_stall_margin': 0.12140190310349164, 'max_loss_coefficient': 0.03301978633508015,
              'part_speed.pressure_ratio_total': 1.1530208764959304,
              'part_speed.efficiency_polytropic': 0.9252745196598068}

# v13 leaves this subsonic NACA65 reference unchanged.
GOLDEN_V13 = dict(GOLDEN_V12)

# v14's shock-cell integration leaves this entirely subsonic reference unchanged.
GOLDEN_V14 = dict(GOLDEN_V13)

# v15 only changes MCA deviation; this NACA65 reference is unchanged.
GOLDEN_V15 = dict(GOLDEN_V14)

# v16 only changes MCA construction; this NACA65 reference is unchanged.
GOLDEN_V16 = dict(GOLDEN_V15)


def test_simulator_goldens(one_stage):
    _, _, result = one_stage
    assert result.simulator_version == "slc_aungier_experimental_v16"
    for key, value in GOLDEN_V16.items():
        assert result.metrics[key] == pytest.approx(value, rel=1e-7), key
