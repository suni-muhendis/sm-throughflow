"""Digitized casing-pressure recovery and a conditioned passage-shock screen."""
from hashlib import sha256
import json

import numpy as np

from sm_throughflow.solver.rows import ExitGeometry
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.passage_shock_candidate import shock
from validation.phase3_rows import V, geometry_file, measured_states, reconstructed_loss, row_model
from validation.probe_compressible_diffusion import BASELINE
from validation.probe_passage_shock import pressure_contours, surfaces
from validation.verify_family_source_v14 import verify


PIXELS = ROOT / "validation/studies/tm79280_figure8_pixels.json"
WINDOWS = {
    "front": (.25, .40),
    "mid": (.45, .60),
    "after_mid": (.60, .75),
    "aft": (.75, .95),
}


def decode_curve(points, x_axis, y_axis, x_range, y_range, tolerance):
    """Convert pixel-centre picks to axial chord fractions and pressure ratios."""
    raw = np.asarray(points, dtype=float)
    x_scale = (x_range[1] - x_range[0]) / (100 * (x_axis[1] - x_axis[0]))
    y_scale = (y_range[1] - y_range[0]) / (y_axis[1] - y_axis[0])
    x = x_range[0] / 100 + (raw[:, 0] - x_axis[0]) * x_scale
    p = y_range[0] + (raw[:, 1] - y_axis[0]) * y_scale
    dx, dp = tolerance * abs(x_scale), tolerance * abs(y_scale)
    if not np.all(np.isfinite((x, p))) or np.any(p <= 0) or np.any(np.diff(x) <= 2 * dx):
        raise ValueError("digitized markers must be physical and remain ordered within the pixel band")
    return x, p, dx, dp


def pressure_at(curve, station):
    """Conservative envelope for a piecewise-linear digitized pressure."""
    x, p, dx, dp = curve
    lo, hi = station - dx, station + dx
    if not x[0] <= lo <= hi <= x[-1]:
        raise ValueError("pressure query is outside the digitized coverage")
    samples = np.r_[np.interp([lo, hi], x, p), p[(lo < x) & (x < hi)]]
    return [float(np.interp(station, x, p)), float(samples.min() - dp), float(samples.max() + dp)]


def difference(a, b):
    """Return b minus a with conservative independent endpoint bands."""
    return [b[0] - a[0], b[1] - a[2], b[2] - a[1]]


def probe_candidate(case, measurement, contours, trailing_pressure):
    """Condition on reported station states, without substituting casing pressure."""
    reading = measurement["reading"]
    inlet, exit, samples = measured_states(
        case.rotor_elements[reading], V.L.read_geometry(geometry_file(case.case_id, 0)),
        measurement["rpm"], measurement["mass_flow"],
    )
    model = row_model(case.design, 0, measurement["rpm"])
    gas = model.gas
    geometry = ExitGeometry(exit.t, exit.y, exit.r, exit.z)
    span, upstream = surfaces(model, inlet, geometry, *contours)
    row = model(inlet, exit, geometry)
    rebuilt = reconstructed_loss(inlet, exit, gas)
    points = {}
    for label, i in (("outermost_measured", -2), ("extrapolated_tip", -1)):
        mach, beta, relative_total = (upstream[key][i] for key in ("mach1", "beta1", "pt1"))
        args = (mach, beta, abs(np.degrees(row.exit_angle[i])), exit.P[i] / relative_total, span[i], gas.gamma)
        entry = dict(inlet_mach=float(mach), exit_back_pressure_ratio=float(args[3]),
                     v16_shock_loss=float(row.diagnostics["shock_loss"][i]),
                     reconstructed_total_loss=float(rebuilt[i]))
        if label == "outermost_measured":
            sample = samples[-1]
            entry["span_from_tip_percent"] = sample.get("PERCENT SPAN", V.RP_SPAN[int(sample["RP"])])
            entry["printed_total_loss"] = samples[-1]["LOSS COEFF TOT"]
        try:
            state = shock(*args)
        except ValueError as exc:
            entry.update(status="unsupported", reason=str(exc))
        else:
            entry.update(status="evaluated_inviscid_research", regime=state["regime"],
                         shock_loss=float(state["loss"]), back_pressure_used=state["back_pressure_used"],
                         axial_casing_profile_available=False)
            if "xd" in state:
                entry["suction_foot_chord_coordinate"] = state["xd"]
            if label == "extrapolated_tip":
                # Account for radius change using rothalpy at fixed inlet
                # entropy, then apply the candidate shock pressure ratio.
                h0r = inlet.I[i] + .5 * (inlet.omega * exit.r[i])**2
                ceiling = state["total_ratio"] * gas.pressure(h0r, inlet.s[i])
                h_at_survey_speed = h0r - .5 * (exit.Wm[i]**2 + exit.W_theta[i]**2)
                if h_at_survey_speed <= 0:
                    raise ValueError("the conditioned exit velocity exceeds the rothalpy budget")
                at_survey_speed = state["total_ratio"] * gas.pressure(h_at_survey_speed, inlet.s[i])
                entry["exit_pressure_ceiling"] = {}
                for normalization, p0 in (("local_inlet", inlet.P0[i]),
                                          ("mass_averaged_inlet", inlet.mass_average(inlet.P0))):
                    ratio = float(ceiling / p0)
                    speed_ratio = float(at_survey_speed / p0)
                    entry["exit_pressure_ceiling"][normalization] = dict(
                        zero_velocity_ratio=ratio,
                        at_conditioned_velocity_ratio=speed_ratio,
                        zero_velocity_below_casing_band=ratio < trailing_pressure[1],
                        at_conditioned_velocity_below_casing_band=speed_ratio < trailing_pressure[1],
                    )
        points[label] = entry
    return points


def evaluate(source):
    results = {}
    for rotor, panel in source["panels"].items():
        case = V.CASES[f"nasa_stage{rotor}"]()
        readings = {p["reading"]: p for p in case.measured_points(100)}
        contours = pressure_contours(case.design, 0)
        records = {}
        for flow, curve in panel["curves"].items():
            point = readings[curve["reading"]]
            if float(flow) != point["mass_flow"]:
                raise ValueError("casing plot and row reading mass flows differ")
            x, p, dx, dp = decode_curve(curve["points"], panel["x_axis_pixels"], panel["y_axis_pixels"],
                                        source["horizontal_axis_percent"], source["vertical_axis_ratio"],
                                        source["digitization_tolerance_pixels"])
            profile = x, p, dx, dp
            rises = {name: difference(pressure_at(profile, a), pressure_at(profile, b))
                     for name, (a, b) in WINDOWS.items()}
            trailing = pressure_at(profile, 1.)
            records[flow] = dict(reading=point["reading"], symbol=curve["symbol"], x_over_axial_chord=x.tolist(),
                                 pressure_ratio=p.tolist(), x_pick_tolerance=dx, p_pick_tolerance=dp,
                                 pressure_rise=rises,
                                 mid_minus_after_mid_rise=difference(rises["after_mid"], rises["mid"]),
                                 trailing_edge_pressure=trailing,
                                 candidate=probe_candidate(case, point, contours, trailing))
        low, high = (records[flow] for flow in (min(records, key=float), max(records, key=float)))
        results[rotor] = dict(curves=records, low_minus_high_pressure_rise={
            name: difference(high["pressure_rise"][name], low["pressure_rise"][name]) for name in WINDOWS
        })
    return results


def summary(results):
    curves = [curve for rotor in results.values() for curve in rotor["curves"].values()]
    outer = [r["candidate"]["outermost_measured"] for r in curves]
    evaluated = [r for r in outer if r["status"] == "evaluated_inviscid_research"]
    over_printed = [r for r in evaluated if r["shock_loss"] > r["printed_total_loss"]]
    return dict(curves=len(curves), selected_markers=sum(len(r["pressure_ratio"]) for r in curves),
                candidate_outermost_evaluated=len(evaluated),
                candidate_outermost_back_pressure_used=sum(r["back_pressure_used"] for r in evaluated),
                candidate_outermost_shock_exceeds_printed=len(over_printed),
                candidate_outermost_shock_exceeds_both=sum(
                    r["shock_loss"] > r["reconstructed_total_loss"] for r in over_printed),
                casing_profiles_available=sum(r["axial_casing_profile_available"] for r in evaluated))


def main():
    identity = verify(BASELINE)
    raw = PIXELS.read_bytes()
    source = json.loads(raw)
    result = evaluate(source)
    if result != evaluate(source):
        raise RuntimeError("the repeated casing and candidate reductions differ")
    output = create_campaign(
        purpose="tm79280_rotor_casing_pressure_and_conditioned_shock",
        selection=dict(research_only=True, training_label_qualified=False,
                       baseline=BASELINE.name, pixels_sha256=sha256(raw).hexdigest(),
                       report=source["source"], report_sha256=source["source_sha256"],
                       pressure_field_qualified=False),
    )
    write_json_new(output / "analysis.json",
                   dict(source=identity, windows=WINDOWS, summary=summary(result), results=result))
    print(output, flush=True)


if __name__ == "__main__":
    main()
