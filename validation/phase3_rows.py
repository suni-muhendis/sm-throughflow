"""Blade-row closures conditioned on experimental inlet AND exit meridional state.

This isolates closure errors; it does not predict meridional velocity, nor does
it independently validate the report's reconstructed rotor-exit conditions.
NASA TP-1338 Appendix B5 and solver RowPerformance use the same inlet-head loss
basis. Printed loss and independently reconstructed loss are both retained.
"""
import hashlib
import json
import math

import numpy as np

from validation.phase3 import PROTOCOL_PATH, plain, V, admission, Simulator
from validation.campaign import create_campaign, write_json_new
from sm_throughflow.contracts import AUNGIER_PROFILES, SPAN_FRACTIONS, ThroughflowDesignV2
from sm_throughflow.provenance import runtime_identity
from sm_throughflow.solver.aungier_row import AungierCompressorRow, BladeSections, TipClearance, ShroudSeal
from sm_throughflow.solver.endwall import sutherland_air
from sm_throughflow.solver.gas import PerfectGas
from sm_throughflow.solver.quasi_normal import StationFlow
from sm_throughflow.solver.rows import ExitGeometry


def row_model(design, index, rpm, gas=None):
    """Production closure with original sections, without whole-annulus admission.

    Only validation assembles a row this way. Equivalence to Simulator.build is
    tested on admissible input; this does not relax production geometry checks.
    """
    design = ThroughflowDesignV2.model_validate(design)
    row = design.rows[index]
    stations = design.passage.stations
    profile = AUNGIER_PROFILES["axial_compressor_aungier_v2"]
    clearance = seal = None
    if row.row_type == "rotor":
        clearance = TipClearance(row.tip_clearance_m, "shroud")
    elif row.hub_clearance_m is not None:
        clearance = TipClearance(row.hub_clearance_m, "hub")
    else:
        r = float(np.interp(row.leading_edge_axial_m, [s.axial_m for s in stations], [s.hub_radius_m for s in stations]))
        s = row.shroud_seal
        seal = ShroudSeal(r, s.clearance_m, s.fin_count, s.fin_pitch_m, s.fin_thickness_m, "hub")
    return AungierCompressorRow(
        BladeSections(SPAN_FRACTIONS, row.metal_angle_in_deg, row.metal_angle_out_deg, row.chord_m, row.thickness_to_chord, coordinate="span"),
        row.blade_count, rpm * 2 * math.pi / 60 if row.row_type == "rotor" else 0, gas or PerfectGas(),
        profile=row.profile, camberline=row.camberline, a_c=row.max_camber_location, row_number=index + 1,
        inlet_guide_vane=row.row_id in design.inlet_guide_vanes(), clearance=clearance, seal=seal,
        throat_over_pitch=Simulator.throat_over_pitch(row, stations), expansion_angle=Simulator.expansion_angles(row, stations),
        shock_surface_angles=Simulator.shock_surface_angles(row, stations),
        section_shape=Simulator.section_shape(row, stations), viscosity=sutherland_air,
        K1=profile["K1"], max_loss=profile["max_loss"], smoothing=profile["smoothing"], shock_mean=profile["shock_mean"],
    )


def extend(x, y, ends, policy="constant"):
    """Explicit unmeasured wall closure, preserving every interior sample."""
    x, y = np.asarray(x), np.asarray(y)
    if len(x) < 2 or not ends[0] < x[0] < x[-1] < ends[1] or np.any(np.diff(x) <= 0):
        raise ValueError("measured samples must be strictly inside ordered wall endpoints")
    if policy == "constant":
        return np.r_[y[0], y, y[-1]]
    if policy == "linear":
        return np.r_[y[0] + (ends[0] - x[0]) * (y[1] - y[0]) / (x[1] - x[0]), y,
                     y[-1] + (ends[1] - x[-1]) * (y[-1] - y[-2]) / (x[-1] - x[-2])]
    raise ValueError("unknown wall extrapolation")


def station(r, z, wm, ct, t0, p0, omega, mass, gas):
    r, z, wm, ct, t0, p0 = [np.asarray(v, dtype=float) for v in (r, z, wm, ct, t0, p0)]
    H = gas.enthalpy(t0)
    h = H - .5 * (wm ** 2 + ct ** 2)
    if np.any(h <= 0) or np.any(p0 <= 0) or np.any(wm <= 0):
        raise ValueError("invalid reconstructed experimental state")
    s = gas.entropy(H, p0)
    return StationFlow(t=(r - r[0]) / (r[-1] - r[0]), y=r-r[0], r=r, z=z, eps=np.zeros_like(r), omega=omega,
                       Wm=wm, C_theta=ct, W_theta=ct-omega*r, h=h, s=s, H=H, I=H-omega*r*ct,
                       T=gas.temperature(h), P=gas.pressure(h, s), rho=gas.density(h, s), a=gas.sound_speed(h),
                       T0=t0, P0=p0, mass_flow=mass, blockage=1.0)


def measured_states(elements, geometry, rpm, mass, rotor=True, policy="constant"):
    rows = sorted(elements, key=lambda row: row["RADII IN"])
    gas, omega = PerfectGas(), rpm * 2 * math.pi / 60 if rotor else 0
    states = []
    for edge, column in (("IN", "I"), ("OUT", "O")):
        rg = np.array([float(g["R" + column]) * .01 for g in geometry])
        zg = np.array([float(g["Z" + column]) * .01 for g in geometry])
        order = np.argsort(rg)
        ends = [float(next(g for g in geometry if g["RP"] == wall)["R" + column]) * .01 for wall in ("HUB", "TIP")]
        r = np.array([v["RADII " + edge] * .01 for v in rows])
        radius = np.r_[ends[0], r, ends[1]]
        z = np.interp(radius, rg[order], zg[order])
        def array(key):
            return np.asarray([v[key] for v in rows])
        wm, ct = array("MERID VEL " + edge), array("TANG VEL " + edge)
        t0, p0 = array("TOTAL TEMP IN"), array("TOTAL PRESS IN") * 1e4
        if edge == "OUT":
            t0, p0 = t0 * array("TOTAL TEMP RATIO"), p0 * array("TOTAL PRESS RATIO")
        states.append(station(radius, z, *(extend(r, v, ends, policy) for v in (wm, ct, t0, p0)), omega, mass, gas))
    return states[0], states[1], rows


def reconstructed_loss(inlet, exit, gas):
    """NASA B5/Aungier inlet relative dynamic-head basis, including radius work."""
    hrel1 = inlet.h + .5 * (inlet.Wm ** 2 + inlet.W_theta ** 2)
    hrel2 = exit.h + .5 * (exit.Wm ** 2 + exit.W_theta ** 2)
    ideal2 = inlet.I + .5 * (inlet.omega * exit.r) ** 2
    return (gas.pressure(ideal2, inlet.s) - gas.pressure(hrel2, exit.s)) / (gas.pressure(hrel1, inlet.s) - inlet.P)


def geometry_file(case_id, row_index):
    config = (V.L.LEWIS_STAGES | V.L.FAN_STAGES)[case_id]
    name = config[("rotor", "stator")[row_index]]
    table = config.get("geometry", ("tableIII", "tableIII"))[row_index]
    return V.L.CASES / case_id / f"{config['report']}_{table}_{name}.csv"


def condition_result(case, speed, p, index, *, policy="constant", uniform=False):
    row_type = ("rotor", "stator")[index]
    elements = (case.rotor_elements, case.stator_elements)[index][p["reading"]]
    geometry = V.L.read_geometry(geometry_file(case.case_id, index))
    inlet, exit, rows = measured_states(elements, geometry, p["rpm"], p["mass_flow"], index == 0, policy)
    gas = PerfectGas()
    if uniform:
        inlet = station(inlet.r, inlet.z, *(np.full_like(inlet.r, inlet.mass_average(getattr(inlet, k))) for k in ("Wm", "C_theta", "T0", "P0")),
                        inlet.omega, inlet.mass_flow, gas)
    model = row_model(case.design, index, p["rpm"], gas)
    performance = model(inlet, exit, ExitGeometry(exit.t, exit.y, exit.r, exit.z))
    d = performance.diagnostics
    predicted_ct = exit.Wm * np.tan(performance.exit_angle) + inlet.omega * exit.r
    measured_euler = inlet.omega * (exit.r * exit.C_theta - inlet.r * inlet.C_theta)
    predicted_work = inlet.omega * (exit.r * predicted_ct - inlet.r * inlet.C_theta)
    # Reconstructed stations contain two unmeasured wall points; report only the
    # measured interior and keep those wall assumptions in the provenance.
    pts = []
    for n, r in enumerate(rows, start=1):
        work = exit.H[n] - inlet.H[n]
        span = r.get("PERCENT SPAN", V.RP_SPAN[int(r["RP"])])
        pts.append(dict(span_from_tip=span, span_inferred_from_radial_position="PERCENT SPAN" not in r, core=15 <= span <= 85,
                        mach=d["relative_inlet_mach"][n], reynolds=d["reynolds_number"][n], loading=r.get("D FACT"),
                        measured_deviation=r.get("DEV"), predicted_deviation=d["deviation"][n],
                        deviation_error=d["deviation"][n]-r["DEV"] if "DEV" in r else None,
                        measured_loss=r.get("LOSS COEFF TOT"), predicted_loss=performance.loss[n],
                        loss_error=performance.loss[n]-r["LOSS COEFF TOT"] if "LOSS COEFF TOT" in r else None,
                        reconstructed_loss=reconstructed_loss(inlet, exit, gas)[n],
                        relative_exit_angle_error_deg=np.degrees(performance.exit_angle[n]-exit.beta[n]),
                        measured_meridional_velocity_ratio=exit.Wm[n]/inlet.Wm[n],
                        conditional_euler_work=predicted_work[n], measured_temperature_work=work, measured_euler_work=measured_euler[n],
                        measured_work_consistency_relative=(measured_euler[n]-work)/work if index == 0 and abs(work) > 1 else None,
                        conditional_work_error_relative=(predicted_work[n]-work)/work if index == 0 and abs(work) > 1 else None,
                        downstream_angle_error_deg=np.degrees(np.arctan2(predicted_ct[n], exit.Wm[n])-exit.alpha[n]),
                        wake_blockage=performance.wake_blockage[n], loss_limit_active=d["loss_limit_active"][n],
                        throat_capacity_margin=d["throat_capacity_margin"][n],
                        incidence_error=d["incidence"][n]-r["INCIDENCE MEAN"] if "INCIDENCE MEAN" in r else None))
    folder = V.L.CASES / case.case_id
    config = (V.L.LEWIS_STAGES | V.L.FAN_STAGES)[case.case_id]
    paths = sorted(folder.glob(f"{config['report']}_table*_{config[row_type]}_reading{p['reading']}.csv"))
    return plain(dict(case=case.case_id, speed=speed, reading=p["reading"], row_type=row_type,
                      blade_family=case.design["rows"][index]["camberline"],
                      machine_family="core_35_38" if case.case_id in V.L.LEWIS_STAGES else "fan_52_55",
                      damper_presence="absent" if case.case_id in V.L.LEWIS_STAGES else "not_mentioned_in_report",
                      status="evaluated_conditional_closure", wall_policy=policy, uniform_inlet=uniform,
                      release_evidence=False, measured_exit_vm_supplied=True,
                      original_admission=admission(case.design), source_files=[str(p.relative_to(V.HERE.parent)).replace("\\", "/") for p in paths],
                      transcription_question_marks=sum(p.read_text().count("?") for p in paths), points=pts))


def run_rows(protocol):
    results = []
    for case_id in protocol["development"]["row_measured_states"]:
        case = V.CASES[case_id]()
        for speed in sorted(case.speeds):
            for p in case.measured_points(speed):
                for index, elements in enumerate((case.rotor_elements, case.stator_elements)):
                    if p["reading"] not in elements:
                        continue
                    try:
                        results.append(condition_result(case, speed, p, index))
                    except Exception as exc:
                        results.append(dict(case=case_id, speed=speed, reading=p["reading"], row_type=("rotor", "stator")[index],
                                            status="experimental_adapter_or_closure_failure", error_type=type(exc).__name__, error=str(exc)))
    case = V.CASES["nasa_stage35"]()
    p = max(case.measured_points(100), key=lambda x: x["stage_eta"])
    sensitivity = [condition_result(case, 100, p, index, policy=policy, uniform=uniform)
                   for index in (0, 1) for policy, uniform in (("constant", False), ("linear", False), ("constant", True))]
    return results, sensitivity


def main():
    protocol = json.loads(PROTOCOL_PATH.read_text())
    if runtime_identity()["source_sha256"] != protocol["production_source_sha256"]:
        raise RuntimeError("production source differs from the preregistered model")
    campaign = create_campaign(purpose="phase3_measured_state_row_closures",
                               selection=dict(protocol_sha256=hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest()))
    write_json_new(campaign / "protocol.json", protocol)
    results, sensitivity = run_rows(protocol)
    write_json_new(campaign / "rows.json", results)
    write_json_new(campaign / "row_sensitivity.json", sensitivity)
    print(campaign, flush=True)
    print("rows", len(results), "evaluated", sum(r["status"] == "evaluated_conditional_closure" for r in results), flush=True)
    for r in results:
        if "error" in r:
            print(r["case"], r["reading"], r["row_type"], r["error"], flush=True)


if __name__ == "__main__":
    main()
