"""Compare the fixed-mass internal-shock branch with the matched NASA records."""
import csv
import hashlib
import json

import numpy as np
from scipy.integrate import cumulative_trapezoid

from sm_throughflow.contracts import ThroughflowDesignV2
from sm_throughflow.correlations.blade_geometry import _stagger, camberline, section
from sm_throughflow.geometry import blade_sections
from sm_throughflow.solver.endwall import sutherland_air
from sm_throughflow.solver.gas import PerfectGas
from validation.audit_rotor_casing_pressure import PIXELS, WINDOWS, decode_curve
from validation.backpressure_passage_reference import (
    PassageDomain, attached_displacement, exit_wake, solve,
)
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3_rows import V, geometry_file, measured_states, reconstructed_loss
from validation.probe_compressible_diffusion import BASELINE
from validation.shock_interaction_evidence import measured_rows
from validation.verify_family_source_v14 import verify


BLOCKAGE = ROOT / "validation/cases/nasa_rotor37_shock_interaction/TM107310_table6.csv"
SUCTION_PICKS = ROOT / "validation/studies/tm107310_figure55_trailing_pixels.json"


def section_profile(row, sec, x):
    """Axial cuts through the blade surfaces and rounded edge circles."""
    upper, lower, edges = section(row.profile, row.camberline, sec["camber"], sec["t_c"],
                                  sec["a_c"], row.edge_radius_to_chord, **sec["shape"])
    edge_curves = np.split(edges, 2)
    segments = [_stagger(c, sec["stagger"]) for c in (upper, lower, *edge_curves)]
    points = np.concatenate(segments)
    x_min, x_max = points[:, 0].min(), points[:, 0].max()
    thickness = np.zeros_like(x)
    for i, z in enumerate(x_min + x * (x_max - x_min)):
        cuts = []
        for curve in segments:
            a, b = curve[:-1], curve[1:]
            select = (np.minimum(a[:, 0], b[:, 0]) <= z) & (z < np.maximum(a[:, 0], b[:, 0]))
            aa, bb = a[select], b[select]
            cuts.extend(aa[:, 1] + (z - aa[:, 0]) * (bb[:, 1] - aa[:, 1]) / (bb[:, 0] - aa[:, 0]))
        if cuts:
            thickness[i] = max(cuts) - min(cuts)
    mean = _stagger(np.column_stack(camberline(row.camberline, sec["camber"], sec["a_c"],
                                                transition=sec["shape"]["transition"],
                                                turning_ratio=sec["shape"]["turning_ratio"])), sec["stagger"])
    if np.any(np.diff(mean[:, 0]) <= 0):
        raise ValueError("axial camberline must be strictly ordered")
    metal = np.arctan(np.gradient(mean[:, 1], mean[:, 0], edge_order=2))
    axial = np.interp(x_min + x * (x_max - x_min), mean[:, 0], metal)
    # Keep the prescribed inlet and exit angles, with the metal-angle
    # curvature as an alternative to straight interpolation.
    turning_shape = axial - ((1 - x) * axial[0] + x * axial[-1])
    return thickness, turning_shape


def sample_pressure(solution, stations):
    """Use separate interpolants at the jump instead of smearing the shock."""
    before = solution.stations < solution.shock_station
    after = solution.stations > solution.shock_station
    stations = np.asarray(stations)
    upstream = np.interp(stations, np.r_[solution.stations[before], solution.shock_station],
                         np.r_[solution.pressure[before], solution.shock_pressure_before])
    downstream = np.interp(stations, np.r_[solution.shock_station, solution.stations[after]],
                           np.r_[solution.shock_pressure_after, solution.pressure[after]])
    return np.where(stations < solution.shock_station, upstream, downstream)


def probe_slice(x, section_data, chord, row, inlet, exit, i, gas, figure):
    thickness, turning = section_data
    radius = (1 - x) * inlet.r[i] + x * exit.r[i]
    pitch = 2 * np.pi * radius / row.blade_count
    height_ratio = np.gradient(exit.r, inlet.r, edge_order=2)[i]
    strip = 1 + x * (height_ratio - 1)
    z_length = exit.z[i] - inlet.z[i]
    path = np.hypot(z_length, exit.r[i] - inlet.r[i])
    total_h = inlet.I[i] + .5 * (inlet.omega * radius)**2
    t0 = total_h / gas.cp
    p0_in = float(gas.pressure(total_h[0], inlet.s[i]))
    inlet_speed = np.hypot(inlet.Wm[i], inlet.W_theta[i])
    mass = inlet.rho[i] * inlet.Wm[i] * pitch[0]
    unit_re = inlet.rho[i] * inlet_speed / sutherland_air(inlet.T[i])
    p_head = p0_in - inlet.P[i]
    ideal_out = float(gas.pressure(total_h[-1], inlet.s[i]))
    result = {}
    for name, shape in (("linear_turning", np.zeros_like(x)), ("metal_curvature", turning)):
        beta = (1 - x) * abs(inlet.beta[i]) + x * abs(exit.beta[i]) + shape
        gap = (pitch - thickness * chord) * np.cos(beta)
        arc = cumulative_trapezoid(path / np.cos(beta), x, initial=0.)
        attached = 2 * attached_displacement(arc, unit_re)
        for layer, delta in (("inviscid", np.zeros_like(x)), ("attached", attached)):
            key = f"{name}_{layer}"
            entry = dict(exit_blockage_hypothesis=float(delta[-1] / gap[-1]),
                         near_te_one_wall_mass_defect_fraction=float(np.interp(.98, x, .5 * delta / gap)),
                         survey_velocity_inferred_exit_blockage=float(
                             1 - mass / (exit.rho[i] * np.hypot(exit.Wm[i], exit.W_theta[i]) * gap[-1] * strip[-1])),
                         exit_pressure_boundary=float(exit.P[i]))
            result[key] = entry
            if inlet_speed <= inlet.a[i]:
                entry["status"] = "inlet_not_supersonic_for_single_shock_branch"
                continue
            try:
                sol = solve(x, strip * gap, t0, mass=mass, inlet_total_pressure=p0_in,
                            exit_pressure=exit.P[i], displacement_area=strip * delta,
                            gamma=gas.gamma, gas_constant=gas.R)
            except PassageDomain as exc:
                entry.update(status=exc.reason, **exc.evidence)
                continue
            entry.update(status="pressure_matched_internal_shock", shock_station=sol.shock_station,
                         shock_mach_before=sol.shock_mach_before, shock_mach_after=sol.shock_mach_after,
                         shock_loss=(ideal_out - sol.exit_total_pressure) / p_head,
                         relative_mass_error=sol.relative_mass_error,
                         relative_exit_pressure_error=sol.relative_exit_pressure_error,
                         axial_chord=x.tolist(), static_pressure_pa=sol.pressure.tolist(), mach=sol.mach.tolist())
            try:
                wake = exit_wake(sol.mach[-1], sol.pressure[-1], t0[-1], sol.exit_blockage,
                                 gamma=gas.gamma, gas_constant=gas.R)
            except ValueError as exc:
                entry.update(wake_status="wake_flux_model_outside_domain", wake_reason=str(exc))
            else:
                entry.update(wake_status="mixed", survey_loss=(ideal_out - wake.mass_average_total_pressure) / p_head,
                             mixed_loss=(ideal_out - wake.total_pressure) / p_head,
                             wake_blockage=wake.blockage, mixing_entropy_over_R=wake.mixing_entropy_over_R)
            if figure is not None:
                coord, observed = figure[:2]
                inside = (coord >= 0) & (coord < 1)
                recovered = inside & (coord > sol.shock_station)
                prediction = sample_pressure(sol, coord[inside]) / inlet.mass_average(inlet.P0)
                error = prediction - observed[inside]
                entry["casing"] = dict(measured_x=coord[inside].tolist(), predicted_ratio=prediction.tolist(),
                                       errors=error.tolist(), rms_error=float(np.sqrt(np.mean(error**2))),
                                       downstream_count=int(np.sum(recovered)), window_pressure_rises={
                    window: float(np.diff(sample_pressure(sol, bounds))[0] / inlet.mass_average(inlet.P0))
                    for window, bounds in WINDOWS.items()
                })
                if np.any(recovered):
                    entry["casing"]["downstream_rms_error"] = float(
                        np.sqrt(np.mean(error[recovered[inside]]**2)))
    return result


def evaluate(source, knots):
    x = np.linspace(0., 1., knots)
    result = {}
    gas = PerfectGas()
    for rotor, panel in source["panels"].items():
        case = V.CASES[f"nasa_stage{rotor}"]()
        design = ThroughflowDesignV2.model_validate(case.design)
        row = design.rows[0]
        measurements = {p["reading"]: p for p in case.measured_points(100)}
        records = {}
        for flow, data in panel["curves"].items():
            reading = data["reading"]
            point = measurements[reading]
            if point["mass_flow"] != float(flow):
                raise ValueError("casing pressure and aerodynamic readings differ")
            inlet, exit, rows = measured_states(
                case.rotor_elements[reading], V.L.read_geometry(geometry_file(case.case_id, 0)),
                point["rpm"], point["mass_flow"],
            )
            figure = decode_curve(data["points"], panel["x_axis_pixels"], panel["y_axis_pixels"],
                                  source["horizontal_axis_percent"], source["vertical_axis_ratio"],
                                  source["digitization_tolerance_pixels"])
            rebuilt = reconstructed_loss(inlet, exit, gas)
            # The near-tip radial sample and extrapolated casing are kept
            # separate. Include Rotor 37's core for the blockage screen.
            indices = (list(range(1, len(inlet.t))) if rotor == "37" else [len(inlet.t)-2, len(inlet.t)-1])
            slices = {}
            sections = blade_sections(row, design.passage.stations, inlet.t[indices])
            for i, sec in zip(indices, sections):
                casing = i == len(inlet.t) - 1
                sample = None if casing else rows[i-1]
                name = "casing_extrapolation" if casing else str(V.RP_SPAN[int(sample["RP"])])
                chord = float(np.interp(inlet.t[i], np.linspace(0., 1., len(row.chord_m)), row.chord_m))
                slices[name] = dict(reconstructed_loss=float(rebuilt[i]),
                                    printed_loss=None if casing else sample["LOSS COEFF TOT"],
                                    variants=probe_slice(x, section_profile(row, sec, x), chord, row, inlet, exit,
                                                         i, gas, figure if casing else None))
            records[flow] = dict(reading=reading, slices=slices)
        result[rotor] = records
    return result


def suction_blockage_screen(picks, rotor37):
    measured = {}
    tolerance = picks["pick_tolerance_pixels"]
    for name, data in picks["curves"].items():
        a, b = data["blockage_0_10_percent_pixels"]
        c, d = data["chord_0_100_percent_pixels"]
        px, py = data["last_marker"]
        blockage = .1 * (px - a) / (b - a)
        error = .1 * tolerance / (b - a)
        measured[name] = dict(chord=(py - c) / (d - c), velocity_blockage=blockage,
                              blockage_digitization_band=[blockage - error, blockage + error])
    # The one-wall velocity defect of this adiabatic power-law wake is
    # bounded by its mass defect. Compare the full range of Stage 37
    # closures rather than equating flows from the two experiments.
    span = 100 - picks["span_percent_from_hub"]
    model_bounds = {}
    for flow, record in rotor37.items():
        variants = next(s["variants"] for label, s in record["slices"].items()
                        if label != "casing_extrapolation" and float(label) == span)
        model_bounds[flow] = {key: value["near_te_one_wall_mass_defect_fraction"]
                              for key, value in variants.items() if key.endswith("_attached")}
    return dict(measured=measured, conditional_velocity_blockage_upper_bounds=model_bounds,
                operating_points_matched_across_reports=False)


def main():
    identity = verify(BASELINE)
    raw = PIXELS.read_bytes()
    source = json.loads(raw)
    result = evaluate(source, 161)
    if result != evaluate(source, 161):
        raise RuntimeError("the passage comparison did not repeat")
    refined = evaluate(source, 321)
    with BLOCKAGE.open(encoding="utf-8", newline="") as stream:
        rows = csv.DictReader(stream)
        next(rows)
        evidence = list(rows)
    payload = dict(source=identity, primary_knots=161, refined_knots=321, nasa_cases=result,
                   refined_cases=refined, suder_blockage=evidence, suder_local_losses=measured_rows(),
                   suder_suction_blockage_screen=suction_blockage_screen(json.loads(SUCTION_PICKS.read_bytes()),
                                                                       result["37"]))
    json.dumps(payload, allow_nan=False)
    output = create_campaign(
        purpose="fixed_mass_back_pressure_passage_nasa_comparison",
        selection=dict(baseline=BASELINE.name, research_only=True, training_label_qualified=False,
                       pixels_sha256=hashlib.sha256(raw).hexdigest(), source=source["source"]),
    )
    write_json_new(output / "analysis.json", payload)
    print(output, flush=True)


if __name__ == "__main__":
    main()
