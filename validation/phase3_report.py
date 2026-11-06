"""Analyze existing Phase 3 campaigns without changing any stored outcomes.

python -m validation.phase3_report COUPLED_CAMPAIGN ROW_CAMPAIGN
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from validation.phase3 import (PROTOCOL_PATH, V, plain, statistics, empirical_gate)
from validation.campaign import ROOT, create_campaign, write_json_new
from sm_throughflow.contracts import ThroughflowDesignV2
from sm_throughflow.geometry import station_grid
from sm_throughflow.solver.gas import PerfectGas
from validation.phase3_rows import geometry_file, measured_states


def average(values):
    values = [x for x in values if x is not None and np.isfinite(x)]
    return float(np.mean(values)) if values else None


def rms(values):
    values = [x for x in values if x is not None and np.isfinite(x)]
    return float(np.sqrt(np.mean(np.square(values)))) if values else None


def quadrature_weights(radius, density, vm):
    """Trapezoidal integration of 2*pi*r*rho*Vm dr over measured span only."""
    r, rho, velocity = map(np.asarray, (radius, density, vm))
    if len(r) < 2 or np.any(np.diff(r) <= 0) or np.any(rho <= 0) or np.any(velocity <= 0):
        raise ValueError("ordered radii and positive mass flux required")
    dr = np.diff(r)
    width = .5 * np.r_[dr[0], dr[:-1]+dr[1:], dr[-1]]
    weights = width * r * rho * velocity
    return weights / weights.sum()


def normalized_shape(values, baseline, weights):
    rise = np.asarray(values) - baseline
    denominator = np.dot(weights, rise)
    if abs(denominator) < 1e-10:
        raise ValueError("undefined normalized shape for zero average rise")
    return rise / denominator - 1


def coupled_profile(result, job):
    case = V.CASES[result["case"]]()
    reading = result["measurement"]["reading"]
    if reading not in case.stator_elements:
        return dict(id=result["id"], status="no_transcribed_exit_profile")
    columns = V.LEVEL2_COLUMNS + ("TANG VEL OUT", "PERCENT SPAN")
    all_rows = case.stator_elements[reading]
    measured = sorted([r for r in all_rows if all(k in r for k in columns)], key=lambda r: r["RADII OUT"])
    if len(measured) < 3:
        return dict(id=result["id"], status="insufficient_exit_profile_samples")
    def vals(key):
        return np.array([r[key] for r in measured])
    # These are blade-element exit quantities, so compare to the stator edge,
    # not silently to a different downstream survey plane.
    _, _, rows = station_grid(ThroughflowDesignV2.model_validate(job["design"]), job["task"]["numerics"]["duct_subdivisions"])
    st = result["stations"][rows["S1"]+1]
    span = vals("PERCENT SPAN")
    def at(values):
        return np.interp(1-span/100, st["t"], values)
    pm = vals("TOTAL PRESS IN") * vals("TOTAL PRESS RATIO") * 1e4
    tm = vals("TOTAL TEMP IN") * vals("TOTAL TEMP RATIO")
    vm = vals("MERID VEL OUT")
    cm = vals("TANG VEL OUT")
    gas = PerfectGas()
    hm = gas.enthalpy(tm) - .5*(vm**2+cm**2)
    rho = gas.density(hm, gas.entropy(gas.enthalpy(tm), pm))
    weight = quadrature_weights(vals("RADII OUT")*.01, rho, vm)
    p, t, velocity = at(st["P0"]), at(st["T0"]), at(st["Wm"])
    angle = at(np.degrees(np.arctan2(st["C_theta"], st["Wm"])))
    pbase, tbase = job["task"]["inlet"]["total_pressure_pa"], job["task"]["inlet"]["total_temperature_k"]
    errs = dict(p0_shape=normalized_shape(p, pbase, weight)-normalized_shape(pm, pbase, weight),
                t0_shape=normalized_shape(t, tbase, weight)-normalized_shape(tm, tbase, weight),
                angle_degrees=angle-vals("ABS BETAM OUT"),
                vm_shape=normalized_shape(velocity, 0, weight)-normalized_shape(vm, 0, weight))
    core = (span >= 15) & (span <= 85)
    return plain(dict(id=result["id"], case=result["case"], speed=result["speed"], status="compared",
                      model_location="stator_trailing_edge", span_from_tip=span, density=rho, quadrature_weights=weight,
                      measured_samples=len(measured), missing_samples=len(all_rows)-len(measured),
                      errors=errs, core_rms={k: rms(v[core]) for k, v in errs.items()},
                      full_measured_span_rms={k: rms(v) for k, v in errs.items()}))


def speed_bin(speed):
    return "below_90" if speed < 90 else "90_to_below_100" if speed < 100 else "100" if speed == 100 else "above_100"


def bin_name(value, edges):
    if value is None or not np.isfinite(value):
        return "unavailable"
    for lo, hi in zip(edges[:-1], edges[1:]):
        if lo <= value < hi:
            return f"[{lo:g},{hi:g})"
    return "outside_frozen_bins"


def row_statistics(rows, protocol):
    """One value per reading/row/cell; radial samples are not independent rigs."""
    cells = defaultdict(list)
    definitions = protocol["frozen_groups"]
    for row in rows:
        if "points" not in row:
            continue
        for p in row["points"]:
            main = dict(row_type=row["row_type"], machine_family=row["machine_family"], blade_family=row["blade_family"],
                        damper_presence=row["damper_presence"], speed=speed_bin(row["speed"]),
                        Mach=bin_name(p["mach"], definitions["relative_inlet_mach_edges"]),
                        Reynolds=bin_name(p["reynolds"], definitions["reynolds_edges"]),
                        loading=bin_name(p["loading"], definitions["diffusion_edges"]), zone="core" if p["core"] else "endwall")
            # Full predeclared cells, plus marginal groups to expose sparse coverage.
            keys = ["joint|" + "|".join(f"{k}={v}" for k, v in main.items())]
            keys += [f"{dim}={value}|row={row['row_type']}|zone={main['zone']}" for dim, value in main.items() if dim not in ("row_type", "zone")]
            keys += [f"case={row['case']}|speed={row['speed']}|row={row['row_type']}|zone={main['zone']}"]
            for key in keys:
                cells[key].append((row["case"], row["reading"], p))
    output = {}
    for key, values in sorted(cells.items()):
        per_reading = defaultdict(list)
        for case, reading, p in values:
            per_reading[(case, reading)].append(p)
        thresholds = protocol["screening_thresholds"]
        metrics = {}
        for metric, threshold in (("deviation_error", "core_deviation_degrees"), ("loss_error", "core_loss_coefficient"),
                                  ("conditional_work_error_relative", "work_rise_relative"),
                                  ("downstream_angle_error_deg", "core_deviation_degrees")):
            means = [average(p[metric] for p in points) for points in per_reading.values()]
            s = statistics(means, thresholds[threshold])
            s["missing_radial_values"] = sum(p[metric] is None for _, _, p in values)
            if s["missing_radial_values"]:
                s["passed"] = False
            s["radial_rms_p90"] = statistics([rms(p[metric] for p in points) for points in per_reading.values()])["absolute_p90"]
            metrics[metric] = s
        machines = sorted(set(case for case, _ in per_reading))
        enough = len(per_reading) >= thresholds["minimum_readings_per_reported_candidate_cell"] and len(machines) >= thresholds["minimum_machines_per_reported_candidate_cell"]
        output[key] = dict(readings=len(per_reading), machines=machines, radial_samples=len(values), metrics=metrics,
                           sufficient_development_support=enough,
                           threshold_scope="core" if "zone=core" in key else "core thresholds shown for reference only; no endwall acceptance gate",
                           diagnostic_deviation_loss_screen_passed="zone=core" in key and enough and metrics["deviation_error"]["passed"] and metrics["loss_error"]["passed"],
                           release_evidence=False)
    return output


def uncertainty_summary(results):
    variants = [r for r in results if r["group"] == "sensitivity"]
    anchor_id = variants[0]["anchor"]
    anchor = next(r for r in results if r["id"] == anchor_id)
    output = dict(anchor=anchor_id, anchor_classification=anchor["classification"], variants=[], observational_bounds={}, ranking=[])
    for r in variants:
        delta = {k: r["metrics"][k]-anchor["metrics"][k] for k in anchor["metrics"]} if r["converged"] and anchor["converged"] else None
        output["variants"].append(dict(id=r["id"], parameter=r["parameter"], value=r["value"], classification=r["classification"], delta=delta))
    p = anchor["measurement"]
    p01, t01 = 101325., 288.15
    pr, tr = p["stage_pr"], p["rotor_tr"]
    # NASA TP1338 p3 sensor bounds. Rotor temperature is translated, so these
    # arithmetic extremes are NOT full experimental uncertainty or confidence.
    pr_range = [(pr*p01-1700)/(p01+100), (pr*p01+1700)/(p01-100)]
    tr_range = [(tr*t01-.6)/(t01+.6), (tr*t01+.6)/(t01-.6)]
    k = PerfectGas().R/PerfectGas().cp
    eta_range = [(pr_range[0]**k-1)/(tr_range[1]-1), (pr_range[1]**k-1)/(tr_range[0]-1)]
    output["observational_bounds"] = dict(source="NASA TP-1338 printed p3, Appendix B; rotor exit inferred",
        mass_flow_kg_s=.3, rpm=30, flow_angle_degrees=1., temperature_k=.6,
        inlet_total_pressure_pa=100, inlet_static_pressure_pa=300, exit_total_pressure_pa=1700, exit_static_pressure_pa=1000,
        stage_pr_instrument_only_interval=pr_range, stage_eta_conditional_instrument_only_interval=eta_range,
        confidence_interval=False, excludes=["covariance", "rotor-exit reconstruction", "transcription ambiguity", "geometry model form"])
    if anchor["converged"]:
        uncertainty = [v for v in output["variants"] if v["parameter"] in ("clearance", "gap", "blockage", "stream_surfaces", "duct_subdivisions")]
        complete = all(v["delta"] is not None and v["classification"] == "converged" for v in uncertainty) and anchor["classification"] == "converged"
        for v in output["variants"]:
            if v["parameter"] not in ("stagger", "chord") or v["delta"] is None:
                continue
            metrics = {}
            for metric in ("stage_pr", "stage_eta"):
                empirical = max(abs(x-pr) for x in pr_range) if metric == "stage_pr" else max(abs(x-p["stage_eta"]) for x in eta_range)
                observed = [abs(q["delta"][metric]) for q in uncertainty if q["delta"] is not None]
                lower_bound = max(observed + [empirical])
                metrics[metric] = dict(delta=v["delta"][metric], observed_uncertainty_lower_bound=lower_bound,
                    comparison="indistinguishable" if abs(v["delta"][metric]) <= lower_bound else "exceeds_sampled_band_but_not_validated")
            output["ranking"].append(dict(id=v["id"], uncertainty_fully_resolved=complete, metrics=metrics, usable_design_improvement=False))
    return output


def compare_family_delta(measured, predicted, thresholds):
    if predicted is None:
        return dict(pressure_delta_passed=False, efficiency_delta_passed=False, nominal_direction="unavailable")
    dp = predicted["stage_pr"] - measured["stage_pr"]
    de = 100 * (predicted["stage_eta"] - measured["stage_eta"])
    return dict(pressure_delta_error=dp, efficiency_delta_error_points=de,
                pressure_delta_passed=abs(dp) <= thresholds["family_delta_pressure_rise_absolute"],
                efficiency_delta_passed=abs(de) <= thresholds["family_delta_efficiency_points"],
                nominal_direction={k: "same_sign" if np.sign(predicted[k]) == np.sign(measured[k]) else "reversed_or_flat_sign" for k in measured})


def family_deltas(results, protocol):
    output = []
    for speed in (70, 100):
        group = sorted([r for r in results if r["group"] == "clearance_family" and r["speed"] == speed], key=lambda r: r["case"])
        base = group[0]
        for r in group[1:]:
            measured = {k: r["measurement"][k]-base["measurement"][k] for k in ("stage_pr", "stage_eta")}
            predicted = {k: r["metrics"][k]-base["metrics"][k] for k in measured} if base["converged"] and r["converged"] else None
            output.append(dict(comparison="clearance_common_measured_flow", speed=speed, base=base["id"], variant=r["id"],
                               measured_delta=measured, predicted_delta=predicted,
                               **compare_family_delta(measured, predicted, protocol["screening_thresholds"]),
                               release_evidence=False, limitation="unmodelled casing recess/damper; not a pure-clearance hardware derivative"))
    for family in ("core_35_38", "fan_52_55"):
        names = protocol["development"]["independent_family_groups"][family]
        group = sorted([r for r in results if r["group"] == "coupled" and r["selection"] == "measured_peak" and r["speed"] == 100 and r["case"] in names], key=lambda r: r["case"])
        base = group[0]
        for r in group[1:]:
            measured = {k: r["measurement"][k]-base["measurement"][k] for k in ("stage_pr", "stage_eta")}
            predicted = {k: r["metrics"][k]-base["metrics"][k] for k in measured} if base["converged"] and r["converged"] else None
            output.append(dict(comparison="family_at_measured_peak_flow", family=family, base=base["id"], variant=r["id"],
                               measured_delta=measured, predicted_delta=predicted,
                               **compare_family_delta(measured, predicted, protocol["screening_thresholds"]),
                               limitation="different geometries and different peak-flow operating points; not a controlled partial derivative", release_evidence=False))
    return output


def holdout_inventory(protocol):
    blockers = {
        "naca_5stage": "Design report/row geometry absent from the local transcription; notes record the unsuccessful source search.",
        "naca_8stage": "No registered case-specific geometry/measurement adapter; design tables must not be treated as measured operating points.",
        "naca_10stage": "No registered case-specific geometry/measurement adapter; multistage matching and gas-scope checks required.",
        "naca_langley_3stage": "Experiments used Freon-12. Air-equivalent design conditions do not validate this fixed dry-air model; gamma/Re similarity and geometry ambiguities remain.",
        "ge_e3_hpc": "Build-specific final geometry, variable vane schedules, bleeds and performance matching required; hot multistage operation exceeds the provisional 400 K total-temperature scope.",
        "nasa_74a": "Only the inlet three-stage group was built/tested; five-stage design tables are not a five-stage experiment. Vane schedules, measured map transcription and gas scope require an adapter.",
        "pw_2stage_fan": "Measured Table XV and survey planes require interpretation/transcription; running clearance is not printed in the two catalogued reports; no registered adapter.",
        "pw_exit_stage_3s": "Measured overall performance IS transcribed (CR159812 Table III), but no registered adapter. Match 3S1/3S2 geometry, running clearances, stations and angle conventions before evaluating.",
        "nasa_lsac": "Seal-clearance measurements and design parameters are present; complete spanwise blade geometry and measured performance profiles/maps are not executable inputs.",
        "utrc_isolated_rotor": "Airfoil coordinate/geometry transcription exists; measured operating profiles, inlet boundary-layer conditions and a qualified isolated-row adapter are still required.",
    }
    out = []
    for name in protocol["holdout_families"]:
        folder = V.L.CASES / name
        files = sorted(p.name for p in folder.glob("*.csv"))
        out.append(dict(family=name, transcribed_csv_files=files, registered_experimental_adapter=name in V.CASES,
                        evaluated=False, independent_acceptance_evidence=False,
                        reason=blockers[name], metadata_source=str((folder/"notes.md").relative_to(ROOT))))
    return out


def measurement_consistency(rows):
    """Expose the uncertainty in treating reduced experimental states as exact.

    Changing the ideal-exit enthalpy convention here is a diagnostic only. It
    does not recalibrate the closure or replace the printed loss observations.
    """
    output, cache = [], {}
    gas = PerfectGas()
    for row in rows:
        if "points" not in row:
            continue
        if row["case"] not in cache:
            cache[row["case"]] = V.CASES[row["case"]]()
        case = cache[row["case"]]
        p = next(p for p in case.measured_points(row["speed"]) if p["reading"] == row["reading"])
        index = 0 if row["row_type"] == "rotor" else 1
        elements = (case.rotor_elements, case.stator_elements)[index][p["reading"]]
        inlet, exit, measured = measured_states(elements, V.L.read_geometry(geometry_file(case.case_id, index)), p["rpm"], p["mass_flow"], index == 0)
        hrel1 = inlet.h + .5*(inlet.Wm**2+inlet.W_theta**2)
        hrel2 = exit.h + .5*(exit.Wm**2+exit.W_theta**2)
        alternate = (gas.pressure(hrel2, inlet.s)-gas.pressure(hrel2, exit.s))/(gas.pressure(hrel1, inlet.s)-inlet.P)
        output.append(dict(case=row["case"], row_type=row["row_type"], speed=row["speed"], reading=row["reading"],
            euler_temperature_work_consistency=statistics(p["measured_work_consistency_relative"] for p in row["points"] if p["core"]),
            conservative_ideal_loss_minus_printed=[p["reconstructed_loss"]-p["measured_loss"] if p["measured_loss"] is not None else None for p in row["points"]],
            actual_relative_enthalpy_ideal_loss_minus_printed=[float(alternate[i+1]-r["LOSS COEFF TOT"]) if "LOSS COEFF TOT" in r else None for i, r in enumerate(measured)],
            interpretation="Diagnostic inconsistency/averaging/convention sensitivity of reduced states; neither is a new independent measurement or a correction to source tables."))
    return output


def render_plots(output, rows, results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
    for case in sorted(set(r["case"] for r in rows)):
        readings = [r for r in rows if r["case"] == case and r["row_type"] == "rotor" and "points" in r]
        for ax, key, label in zip(axes, ("deviation_error", "conditional_work_error_relative"), ("Core deviation error (deg)", "Conditional rotor work error (%)")):
            x = [r["speed"] for r in readings]
            y = [average(p[key] for p in r["points"] if p["core"]) for r in readings]
            ax.scatter(x, np.array(y)*(100 if "work" in key else 1), s=25, alpha=.7, label=case.replace("nasa_", ""))
            ax.axhline(0, color="k", lw=.7)
            ax.set(xlabel="Speed (% design)", ylabel=label)
            ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Measured-state closures: diagnostic development data, not an accepted domain")
    fig.savefig(output / "row_errors.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
    for case in sorted(set(r["case"] for r in results if r["group"] == "coupled")):
        requested = [r for r in results if r["case"] == case and r["group"] == "coupled"]
        group = [r for r in requested if r["converged"]]
        label = case.replace("nasa_", "") + f" ({len(group)}/{len(requested)})"
        for ax, key in zip(axes, ("stage_pr", "stage_eta")):
            ax.scatter([r["measurement"][key] for r in group], [r["metrics"][key] for r in group], label=label, alpha=.7)
            ax.set(xlabel="Experiment: " + key, ylabel="Projected-input model: " + key)
            ax.grid(alpha=.2)
    for ax in axes:
        lim = [min(*ax.get_xlim(), *ax.get_ylim()), max(*ax.get_xlim(), *ax.get_ylim())]
        ax.plot(lim, lim, "k--", lw=.8)
    axes[0].legend(fontsize=8)
    fig.suptitle("Converged points shown; legend gives converged/requested coverage")
    fig.savefig(output / "overall_errors.png", dpi=170)
    plt.close(fig)


def analyze(coupled, row_campaign):
    protocol = json.loads(PROTOCOL_PATH.read_text())
    evidence = {}
    for path in (coupled, row_campaign):
        if json.loads((path / "protocol.json").read_text()) != protocol:
            raise ValueError("cannot pool different protocols")
        manifest = json.loads((path / "manifest.json").read_text())
        if manifest["runtime"]["source_sha256"] != protocol["production_source_sha256"]:
            raise ValueError("cannot pool different production sources")
        if hashlib.sha256((path / "source.zip").read_bytes()).hexdigest() != manifest["archive_sha256"]:
            raise ValueError("input source archive checksum mismatch")
        for file in sorted(path.rglob("*.json")):
            evidence[file.relative_to(ROOT).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    results = [json.loads(p.read_text()) for p in sorted((coupled / "results").glob("*.json"))]
    inventory = json.loads((coupled / "inventory.json").read_text())
    jobs = {j["id"]: j for j in json.loads((coupled / "jobs.json").read_text())}
    if len(jobs) != len(results) or set(jobs) != {r["id"] for r in results}:
        raise ValueError("campaign incomplete: every requested outcome must be present")
    rows = json.loads((row_campaign / "rows.json").read_text())
    output = create_campaign(purpose="phase3_evidence_analysis_no_calibration", selection=dict(
        coupled_campaign=coupled.name, row_campaign=row_campaign.name,
        protocol_sha256=hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest()))
    write_json_new(output / "input_evidence_sha256.json", evidence)
    threshold = protocol["screening_thresholds"]
    overall = {}
    for case in sorted(set(r["case"] for r in results if r["group"] == "coupled")):
        group = [r for r in results if r["case"] == case and r["group"] == "coupled"]
        stats = {key: statistics([r.get("errors", {}).get(key) for r in group], threshold[gate]) for key, gate in
                 (("stage_pr_rise", "pressure_rise_relative"), ("rotor_tr_rise", "work_rise_relative"), ("stage_eta_points", "efficiency_percentage_points"))}
        overall[case] = dict(requested=len(group), converged=sum(r["converged"] for r in group),
                             limit_free=sum(r["classification"] == "converged" for r in group),
                             classifications=dict(Counter(r["classification"] for r in group)), statistics=stats)
    profiles = []
    for result in results:
        if result["group"] == "coupled" and result["converged"]:
            profiles.append(coupled_profile(result, jobs[result["id"]]))
    valid = [r for r in results if r["group"] == "coupled"]
    rows_summary = row_statistics(rows, protocol)
    profiles_ok = len(profiles) == len(valid) and all(p["status"] == "compared" and p["missing_samples"] == 0 and
        p["core_rms"]["p0_shape"] <= threshold["core_p0_t0_shape_rms"] and p["core_rms"]["t0_shape"] <= threshold["core_p0_t0_shape_rms"] and
        p["core_rms"]["angle_degrees"] <= threshold["core_exit_angle_rms_degrees"] for p in profiles)
    gate = empirical_gate(admission_passed=False, coverage=sum(r["classification"] == "converged" for r in valid)/len(valid),
                          error_passed=all(s["passed"] for case in overall.values() for s in case["statistics"].values()),
                          profiles_passed=profiles_ok, response_passed=False, uncertainty_resolved=False,
                          holdout_families=0, thresholds=threshold)
    summary = dict(protocol=protocol["protocol_version"], original_geometry_admitted=sum(r["original_admission"]["passed"] for r in inventory), registered_machines=len(inventory),
                   total_jobs=len(results), classifications=dict(Counter(r["classification"] for r in results)),
                   coupled_requested=len(valid), coupled_converged=sum(r["converged"] for r in valid),
                   coupled_limit_free=sum(r["classification"] == "converged" for r in valid),
                   projected_admitted_requested=sum(r["effective_admission"]["passed"] for r in valid),
                   projected_admitted_converged=sum(r["effective_admission"]["passed"] and r["converged"] for r in valid),
                   measured_state_rows=len(rows), evaluated_row_closures=sum("points" in r for r in rows),
                   joint_core_cells=sum(k.startswith("joint|") and "zone=core" in k for k in rows_summary),
                   joint_core_cells_with_support=sum(k.startswith("joint|") and "zone=core" in k and v["sufficient_development_support"] for k, v in rows_summary.items()),
                   joint_core_cells_passing_deviation_and_loss=sum(k.startswith("joint|") and v["diagnostic_deviation_loss_screen_passed"] for k, v in rows_summary.items()),
                   overall=overall, gate=gate, qualified_operating_envelope=None, score_enabled=False,
                   row_conditions={k: [min(p[k] for r in rows if "points" in r for p in r["points"] if p[k] is not None), max(p[k] for r in rows if "points" in r for p in r["points"] if p[k] is not None)] for k in ("mach", "reynolds", "loading")},
                   sources=dict(coupled=str(coupled.relative_to(ROOT)), rows=str(row_campaign.relative_to(ROOT))))
    failures = [dict(id=r["id"], case=r["case"], group=r["group"], speed=r["speed"],
                     classification=r["classification"], effective_admission=r["effective_admission"],
                     diagnostics=r["diagnostics"]) for r in results if not r["converged"]]
    for name, value in (("summary", summary), ("row_groups", rows_summary), ("profiles", profiles),
                        ("uncertainty", uncertainty_summary(results)), ("family_deltas", family_deltas(results, protocol)),
                        ("holdout_inventory", holdout_inventory(protocol)), ("failures", failures),
                        ("measurement_consistency", measurement_consistency(rows))):
        write_json_new(output / (name + ".json"), plain(value))
    render_plots(output, rows, results)
    print(output, flush=True)
    print(json.dumps(plain(summary), indent=2), flush=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coupled", type=Path)
    parser.add_argument("rows", type=Path)
    args = parser.parse_args()
    analyze(args.coupled.resolve(), args.rows.resolve())
