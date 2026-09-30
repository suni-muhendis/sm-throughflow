"""Adapter-equivalence cases for the NASA OptTurb and Mattingly examples.

REFERENCE and COMPRESSOR_REFERENCE were produced by executing
``examples/optturb-turbine/optturb-fixed_pressure_loss2.py`` and
``examples/mattingly-axial-compressor/example9.1.py`` directly at
suni-muhendis/turbo-design v1.4.4-sm.2 with moving streamlines disabled. The
remaining values are characterization goldens of simulator
nasa_turbo_design_experimental_v4. This validates translation, not
experimental physics.
"""
import contextlib
import io
import pytest

from scripts.run_throughflow import build_case
from scripts.run_throughflow_compressor import build_case as build_compressor_case
from scripts.run_throughflow_compressor_benchmark import _candidate_case, run_comparison
from scripts.run_throughflow_resolution_study import run_study
from sm_core import make_env
from sm_throughflow.profiles import BACKEND_REVISION

REFERENCE={"power_W":3573397.2318285243,"pressure_ratio_total":3.403251731879399,"efficiency_polytropic":0.7726742175259408}
COMPRESSOR_REFERENCE={"power_W":527722.9442221978,"pressure_ratio_total":1.321457700451021,"efficiency_polytropic":1.0043849643395577}
MULTISTAGE_COMPRESSOR_REFERENCE={"power_W":1016875.9895517118,"pressure_ratio_total":1.6809072464223875,"efficiency_polytropic":1.008996170130541}

CANDIDATE_COMPRESSOR_XFAIL = pytest.mark.xfail(
    strict=True,
    reason=(
        "The Mattingly candidate case has no inlet metal angles (0 deg, 30-55 deg incidence); "
        "since v1.4.4-sm.2 applies stator deviation, its stators choke. A zero-incidence redesign "
        "then fails on turbo-design's compressor energy error (a stator raises the mass-averaged "
        "T0 by 0.62 K). See docs/compressor_validation.md."
    ),
)

def test_optturb_adapter_matches_direct_upstream_solve():
    pytest.importorskip("turbodesign")
    design,task=build_case(1,streamtubes=2)
    with contextlib.redirect_stdout(io.StringIO()):
        result=make_env("turbomachinery_throughflow").evaluate("validation",task,"optturb",design)
    assert result.status=="success"
    for name,expected in REFERENCE.items():
        assert result.metrics[name]==pytest.approx(expected,rel=1e-12,abs=1e-9)
    assert result.metrics["stage_count"]==1.0
    assert result.metrics["streamline_count"]==3.0
    assert result.raw_simulation_output["physics_profile"]["profile_id"]=="optturb_turbine_regression_v1"
    assert result.raw_simulation_output["physics_profile"]["backend_revision"]==BACKEND_REVISION
    assert result.score.normalized_total==0.0

def test_two_stage_compressor_with_ten_streamtubes_is_deterministic():
    pytest.importorskip("turbodesign")
    design,task=build_compressor_case(stages=2,streamtubes=10)
    results=[]
    for _ in range(2):
        with contextlib.redirect_stdout(io.StringIO()):
            results.append(make_env("turbomachinery_throughflow").evaluate("validation",task,"compressor_2_stage",design))
    for result in results:
        assert result.status=="success"
        for name,expected in MULTISTAGE_COMPRESSOR_REFERENCE.items():
            assert result.metrics[name]==pytest.approx(expected,rel=1e-12,abs=1e-9)
        assert result.metrics["stage_count"]==2.0
        assert result.metrics["streamline_count"]==11.0
        assert result.metrics["streamtube_count"]==10.0
        assert len(result.raw_simulation_output["rows"])==4
        assert all(len(row["P0"])==11 for row in result.raw_simulation_output["rows"])
        assert all(len(row["metal_angle_in_deg"])==11 for row in result.raw_simulation_output["rows"])
        assert all(len(row["metal_angle_out_deg"])==11 for row in result.raw_simulation_output["rows"])
    assert results[0].metrics==results[1].metrics
    assert results[0].raw_simulation_output["rows"]==results[1].raw_simulation_output["rows"]

def test_ten_streamtube_resolution_gap_is_reported_for_the_regression_case():
    pytest.importorskip("turbodesign")
    with contextlib.redirect_stdout(io.StringIO()):
        report=run_study(stages=2,streamtube_counts=[10,20])
    assert report["physical_validation"] is False
    coarse=report["observations"][0]
    assert coarse["status"]=="success"
    differences=coarse["relative_difference_to_finest"]
    assert differences["power_W"]==pytest.approx(.019736764521936585,rel=1e-10)
    assert differences["pressure_ratio_total"]==pytest.approx(.006696030593368838,rel=1e-10)
    assert differences["efficiency_polytropic"]==pytest.approx(.0005562063560768022,rel=1e-10)

def test_all_eleven_metal_angle_values_reach_the_nasa_rows_without_resampling():
    pytest.importorskip("turbodesign")
    design,task=build_compressor_case(stages=1,streamtubes=10)
    rotor_in=[float(index) for index in range(11)]
    rotor_out=[-24.0+0.1*index for index in range(11)]
    design["rows"][1]["metal_angle_in_deg"]=rotor_in
    design["rows"][1]["metal_angle_out_deg"]=rotor_out
    with contextlib.redirect_stdout(io.StringIO()):
        result=make_env("turbomachinery_throughflow").evaluate("validation",task,"radial_angles",design)
    assert result.status=="success"
    nasa_rotor=result.raw_simulation_output["rows"][0]
    assert nasa_rotor["metal_angle_in_deg"]==pytest.approx(rotor_in)
    assert nasa_rotor["metal_angle_out_deg"]==pytest.approx(rotor_out)

def test_mattingly_compressor_adapter_matches_direct_upstream_solve():
    pytest.importorskip("turbodesign")
    design,task=build_compressor_case(streamtubes=2)
    with contextlib.redirect_stdout(io.StringIO()):
        result=make_env("turbomachinery_throughflow").evaluate("validation",task,"mattingly_9_1",design)
    assert result.status=="success"
    for name,expected in COMPRESSOR_REFERENCE.items():
        assert result.metrics[name]==pytest.approx(expected,rel=1e-12,abs=1e-9)
    assert result.metrics["stage_count"]==1.0
    assert result.metrics["streamline_count"]==3.0
    assert result.metrics["efficiency_polytropic"]>1.0
    assert result.score.normalized_total==0.0

def test_backend_carter_deviation_matches_documented_algebra():
    import numpy as np
    from turbodesign.deviation import CarterDeviation
    class Row:
        percent_hub_shroud=np.linspace(0.0,1.0,11)
        metal_inlet_angle=[50.0]*11
        metal_exit_angle=[30.0]*11
        solidity=np.asarray([1.0]*11)
    assert CarterDeviation()(Row(),None)==pytest.approx([5.0]*11)

@CANDIDATE_COMPRESSOR_XFAIL
def test_compressor_candidate_applies_spanwise_geometry_loss_and_deviation():
    pytest.importorskip("turbodesign")
    design,task=build_compressor_case(stages=2,streamtubes=10)
    for row in design["rows"]:
        if row["row_type"] not in ("rotor","stator"):
            continue
        row["stagger_angle_deg"]=[30.0+index for index in range(11)]
        row["trailing_edge_thickness_m"]=0.0005
        if row["row_type"]=="rotor":
            row["tip_clearance_m"]=0.0005
    task["physics_profile"]="axial_compressor_candidate_v1"
    task["physics"]={"default_loss_model":"diffusion","default_deviation_model":"carter"}
    with contextlib.redirect_stdout(io.StringIO()):
        result=make_env("turbomachinery_throughflow").evaluate("validation",task,"physical_compressor",design)
    assert result.status=="success"
    assert result.score.normalized_total==0.0
    assert result.raw_simulation_output["physics_profile"]["nominal_deviation_model"]=="carter"
    for row in result.raw_simulation_output["rows"]:
        assert any(abs(value)>1e-6 for value in row["deviation_deg"])
        assert max(row["solidity"])-min(row["solidity"])>1e-3
    assert any(any(value>0 for value in row["Yp"]) for row in result.raw_simulation_output["rows"])


@CANDIDATE_COMPRESSOR_XFAIL
def test_public_compressor_comparison_runs_with_convergence_evidence():
    pytest.importorskip("turbodesign")
    report = run_comparison()
    assert len(report["runs"]) == 4
    assert all(run["status"] == "success" for run in report["runs"])
    for run in report["runs"]:
        metrics = run["metrics"]
        assert metrics["solver_solution_change"] <= 1e-6
        assert metrics["streamline_count"] == 11.0
        assert metrics["streamtube_count"] == 10.0
        assert metrics["massflow_residual"] <= 1e-6
        assert "pressure_ratio_relative_error" in metrics
    regression = report["runs"][0]
    assert regression["metrics"]["pressure_ratio_total"] == pytest.approx(1.3, rel=0.02)
    for run in report["runs"]:
        if "candidate" in run["label"]:
            assert 0.0 < run["metrics"]["efficiency_polytropic"] <= 1.0


def test_compressor_rejects_a_solution_outside_its_residual_tolerance():
    pytest.importorskip("turbodesign")
    design, task = build_compressor_case(stages=1, streamtubes=10)
    task["numerics"]["residual_tolerance"] = 1e-10
    with contextlib.redirect_stdout(io.StringIO()):
        result = make_env("turbomachinery_throughflow").evaluate(
            "validation", task, "strict_residual", design
        )
    assert result.status == "simulation_error"
    assert "massflow residual" in result.error_message


def test_candidate_rejects_polytropic_efficiency_above_unity(monkeypatch):
    # No design is known to reach efficiency above one on the fork's candidate
    # physics, so the backend's value is forced to exercise the gate itself.
    pytest.importorskip("turbodesign")
    from turbodesign.compressor_spool import CompressorSpool
    design, task = _candidate_case(1)
    monkeypatch.setattr(CompressorSpool, "overall_polytropic_efficiency", lambda self: 1.0078)
    with contextlib.redirect_stdout(io.StringIO()):
        result = make_env("turbomachinery_throughflow").evaluate(
            "validation", task, "nonphysical_efficiency", design
        )
    assert result.status == "simulation_error"
    assert "non-physical polytropic efficiency 1.007800" in result.error_message


def test_compressor_reports_an_exhausted_iteration_limit():
    pytest.importorskip("turbodesign")
    design, task = build_compressor_case(stages=2, streamtubes=10)
    task["numerics"]["max_iterations"] = 3
    with contextlib.redirect_stdout(io.StringIO()):
        result = make_env("turbomachinery_throughflow").evaluate(
            "validation", task, "iteration_limit", design
        )
    assert result.status == "simulation_error"
    assert "did not converge in 3 iterations" in result.error_message
