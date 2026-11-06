"""Preregistered v8 empirical audit, with no production-model changes.

Run from the repository: .venv/Scripts/python -m validation.phase3 --workers 3
Every run creates a new immutable campaign. Projected machines are research
inputs, never substitutes for admission of the original experimental geometry.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np

from validation import run as V
from validation.campaign import ROOT, create_campaign, write_json_new
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.drc import run_drc
from sm_throughflow.outcomes import failure_evidence
from sm_throughflow.provenance import runtime_identity
from sm_throughflow.simulator import SlcAungierSimulator as Simulator
from sm_throughflow.solver.limits import solution_limits

PROTOCOL_PATH = Path(__file__).with_name("phase3_protocol.json")


def plain(value):
    """JSON telemetry: unavailable/non-finite diagnostics are null, never zero."""
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [plain(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if np.isfinite(value) else None
    return value


def projected_geometry(design):
    """Replace only in-row wall contours by edge-to-edge straight segments."""
    result = deepcopy(design)
    old = design["passage"]["stations"]
    x = np.array([s["axial_m"] for s in old])
    edges = [r[k] for r in design["rows"] for k in ("leading_edge_axial_m", "trailing_edge_axial_m")]
    nodes = sorted(set(x.tolist() + edges))
    nodes = [z for z in nodes if not any(r["leading_edge_axial_m"] < z < r["trailing_edge_axial_m"] for r in design["rows"])]
    names = ("hub_radius_m", "shroud_radius_m")
    result["passage"]["stations"] = [dict(axial_m=z, **{k: float(np.interp(z, x, [s[k] for s in old])) for k in names}) for z in nodes]
    # Dense sampling also catches extrema of the annulus-area difference.
    sample = np.unique(np.r_[x, nodes, np.linspace(x[0], x[-1], 4001)])
    before = np.array([np.interp(sample, x, [s[k] for s in old]) for k in names])
    after = np.array([np.interp(sample, nodes, [s[k] for s in result["passage"]["stations"]]) for k in names])
    area = before[1] ** 2 - before[0] ** 2
    return result, dict(
        rule="edge_to_edge_wall_projection_inside_rows_only", release_evidence=False,
        original_stations=len(old), projected_stations=len(nodes),
        max_wall_displacement_m=float(np.max(np.abs(after - before))),
        max_wall_displacement_over_local_span=float(np.max(np.abs(after - before) / (before[1] - before[0]))),
        max_relative_annulus_area_change=float(np.max(np.abs((after[1] ** 2 - after[0] ** 2) / area - 1))),
    )


def admission(design):
    return deepcopy(_admission_cached(json.dumps(design, sort_keys=True, allow_nan=False)))


@lru_cache(maxsize=128)
def _admission_cached(serialized):
    design = json.loads(serialized)
    try:
        passed, reason = run_drc(ThroughflowDesignV2.model_validate(design))
        return dict(passed=passed, reason=reason)
    except Exception as exc:
        return dict(passed=False, reason=str(exc), exception_type=type(exc).__name__)


def task_for(point, blockage, protocol):
    task = V.L.task([("measurement", point["mass_flow"], point["rpm"])], inlet_blockage=blockage)
    task.setdefault("numerics", {}).update(protocol["numerics"])
    return task


def interpolate_observation(points, mass_flow):
    points = sorted(points, key=lambda p: p["mass_flow"])
    x = [p["mass_flow"] for p in points]
    if len(set(x)) != len(x) or not x[0] <= mass_flow <= x[-1]:
        raise ValueError("measurement interpolation requires unique flows and no extrapolation")
    out = {k: float(np.interp(mass_flow, x, [p[k] for p in points])) for k in points[0] if k != "reading"}
    out.update(reading="interpolated_inside_common_interval", mass_flow=mass_flow)
    return out


def gap_variant(design, factor):
    """Translate the stator and downstream contour, stretch only its inlet gap."""
    result = deepcopy(design)
    rotor, stator = result["rows"][:2]
    start, end = rotor["trailing_edge_axial_m"], stator["leading_edge_axial_m"]
    shift = (end - start) * (factor - 1)
    for s in result["passage"]["stations"]:
        z = s["axial_m"]
        s["axial_m"] = z + shift * float(np.clip((z - start) / (end - start), 0, 1))
    for row in result["rows"][1:]:
        for key in ("leading_edge_axial_m", "trailing_edge_axial_m"):
            row[key] += shift
    return result


def build_jobs(protocol, progress=None):
    jobs, inventory = [], []
    for case_id, factory in V.CASES.items():
        case = factory()
        design, projection = projected_geometry(case.design)
        inventory.append(dict(case=case_id, original_admission=admission(case.design), projected_admission=admission(design),
                              projection=projection, speeds=sorted(case.speeds),
                              measured_points=sum(len(case.measured_points(s)) for s in case.speeds)))
        if progress:
            progress("geometry checked: " + case_id)
        if case_id not in protocol["development"]["coupled_projected_inputs"]:
            continue
        for speed in sorted(case.speeds):
            points = case.measured_points(speed)
            selection = {max(points, key=lambda p: p["stage_eta"])["reading"]: "measured_peak"}
            if case_id == "nasa_stage35":
                for p in (min(points, key=lambda p: p["mass_flow"]), max(points, key=lambda p: p["mass_flow"])):
                    selection.setdefault(p["reading"], "measured_flow_endpoint")
            for p in points:
                if p["reading"] in selection:
                    jobs.append(dict(id=f"{case_id}_{speed}_{p['reading']}", case=case_id, speed=speed,
                                     group="coupled", selection=selection[p["reading"]], measurement=p,
                                     design=design, task=task_for(p, case.inlet_blockage(speed), protocol),
                                     efficiency_temperature_basis=case.STAGE_ETA_TR, projection=projection))
    family = [V.CASES[k]() for k in protocol["development"]["clearance_family"]]
    for speed in (70, 100):
        lo = max(min(p["mass_flow"] for p in c.measured_points(speed)) for c in family)
        hi = min(max(p["mass_flow"] for p in c.measured_points(speed)) for c in family)
        if lo > hi:
            raise ValueError("no common measured clearance interval")
        mass = (lo + hi) / 2
        for case in family:
            p = interpolate_observation(case.measured_points(speed), mass)
            design, projection = projected_geometry(case.design)
            jobs.append(dict(id=f"{case.case_id}_{speed}_common", case=case.case_id, speed=speed, group="clearance_family",
                             measurement=p, design=design, task=task_for(p, case.inlet_blockage(speed), protocol),
                             efficiency_temperature_basis=case.STAGE_ETA_TR, projection=projection,
                             common_flow_interval=[lo, hi], unmodelled="casing recess and part-span damper"))
    anchor = next(j for j in jobs if j["case"] == "nasa_stage35" and j["speed"] == 100 and j["selection"] == "measured_peak")
    variants = []
    for name, values in (("clearance", protocol["uncertainty"]["clearance_factors"]),
                         ("gap", protocol["uncertainty"]["row_gap_factors"]),
                         ("blockage", protocol["uncertainty"]["inlet_blockage_offsets"]),
                         ("stagger", protocol["design_sensitivity"]["rotor_stagger_degrees"]),
                         ("chord", protocol["design_sensitivity"]["rotor_chord_factors"]),
                         ("stream_surfaces", [21]), ("duct_subdivisions", [4]), ("repeat", [0])):
        for value in values:
            j = deepcopy(anchor)
            j.update(id=f"anchor_{name}_{value}", group="sensitivity", parameter=name, value=value, anchor=anchor["id"])
            rotor = j["design"]["rows"][0]
            if name == "clearance":
                rotor["tip_clearance_m"] *= value
            elif name == "gap":
                j["design"] = gap_variant(j["design"], value)
            elif name == "blockage":
                j["task"]["physics"]["inlet_blockage"] += value
            elif name == "stagger":
                for key in ("metal_angle_in_deg", "metal_angle_out_deg"):
                    rotor[key] = [x + value for x in rotor[key]]
            elif name == "chord":
                rotor["chord_m"] = [x * value for x in rotor["chord_m"]]
            elif name in ("stream_surfaces", "duct_subdivisions"):
                j["task"]["numerics"][name] = value
            variants.append(j)
    jobs += variants
    for job in jobs:
        job["effective_admission"] = admission(job["design"])
        job["release_evidence"] = False
    return jobs, inventory


def report_overall(sol, gas, temperature_basis):
    inlet = sol.stations[0]
    r = next(row for row in sol.rows if row.name == "R1")
    rotor, stage = sol.stations[r.inlet + 1], sol.stations[-1]
    k = gas.R / gas.cp
    result = {}
    for name, st in (("rotor", rotor), ("stage", stage)):
        result[name + "_pr"] = st.mass_average((st.P0 / inlet.P0) ** k) ** (1 / k)
        result[name + "_tr"] = st.mass_average(st.T0 / inlet.T0)
    result["rotor_eta"] = (result["rotor_pr"] ** k - 1) / (result["rotor_tr"] - 1)
    result["stage_eta"] = (result["stage_pr"] ** k - 1) / (result[temperature_basis] - 1)
    return result


def evaluate_job(job):
    start = perf_counter()
    out = {k: v for k, v in job.items() if k not in ("design", "task")}
    try:
        design, task = ThroughflowDesignV2.model_validate(job["design"]), ThroughflowTaskV2.model_validate(job["task"])
        flow, models, sol, balances, seed = Simulator.solve_state(design, task, task.operating_points[0])
        limits = solution_limits(sol)
        out.update(converged=True, classification="converged_with_model_limit" if limits["stall_criterion_crossed"] or limits["throat_capacity_exceeded"] else "converged",
                   metrics=report_overall(sol, flow.gas, job["efficiency_temperature_basis"]),
                   diagnostics=dict(verification=balances, limits=limits, attempts=sol.convergence.attempts, effort=sol.convergence.effort,
                                    repositioning=sol.convergence.repositioning,
                                    endwalls=[] if sol.endwall is None else sol.endwall.convergence),
                   stations=[{k: getattr(st, k) for k in ("t", "r", "z", "Wm", "C_theta", "rho", "T", "P", "T0", "P0", "blockage")} for st in sol.stations],
                   row_diagnostics={key: perf.diagnostics for key, perf in sol.performance.items()})
        out["errors"] = V.errors(out["metrics"], job["measurement"])
    except Exception as exc:
        out.update(converged=False, metrics={}, diagnostics=failure_evidence(exc))
        out["classification"] = out["diagnostics"]["classification"]
    out["elapsed_seconds"] = perf_counter() - start
    return plain(out)


def statistics(values, limits=None):
    values = list(values)
    a = np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=float)
    result = dict(count=len(a), unavailable=len(values) - len(a), bias=None, sample_spread=None, absolute_p90=None, passed=False)
    if len(a):
        result.update(bias=float(np.mean(a)), sample_spread=float(np.std(a, ddof=1)) if len(a) > 1 else None,
                      absolute_p90=float(np.quantile(np.abs(a), .9)))
    if limits and len(a) >= 2 and result["unavailable"] == 0:
        result["passed"] = (abs(result["bias"]) <= limits["absolute_bias"] and result["sample_spread"] <= limits["sample_spread"]
                            and result["absolute_p90"] <= limits["absolute_p90"])
    return result


def empirical_gate(*, admission_passed, coverage, error_passed, profiles_passed,
                   response_passed, uncertainty_resolved, holdout_families, thresholds):
    gates = dict(admission=admission_passed, coverage=coverage >= thresholds["minimum_solution_coverage"],
                 absolute_and_spread=error_passed, radial_profiles=profiles_passed, design_response=response_passed,
                 uncertainty=uncertainty_resolved, independent_holdout=holdout_families >= thresholds["minimum_independent_holdout_families"])
    return dict(qualified=all(gates.values()), gates=gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("workers must be between 1 and 4")
    protocol = json.loads(PROTOCOL_PATH.read_text())
    if runtime_identity()["source_sha256"] != protocol["production_source_sha256"]:
        raise RuntimeError("production source differs from the preregistered model")
    jobs, inventory = build_jobs(protocol, progress=lambda s: print(s, flush=True))
    campaign = create_campaign(purpose="phase3_coupled_projected_research_and_design_sensitivity",
                               selection=dict(protocol_sha256=hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(), jobs=len(jobs)))
    write_json_new(campaign / "protocol.json", protocol)
    write_json_new(campaign / "jobs.json", jobs)
    write_json_new(campaign / "inventory.json", inventory)
    print(str(campaign), flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(evaluate_job, j): j for j in jobs}
        for done in as_completed(pending):
            result = done.result()
            write_json_new(campaign / "results" / (result["id"] + ".json"), result)
            print(result["id"], result["classification"], round(result["elapsed_seconds"], 1), flush=True)
    print("COMPLETE", str(campaign), flush=True)


if __name__ == "__main__":
    main()
