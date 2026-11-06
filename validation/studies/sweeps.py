"""Study 4: smoothness and direction of the response to one design parameter at a time.

Around each baseline, one parameter of the first rotor (or the first stator after it, or the
operating mass flow) is stepped through a range while everything else stays fixed. Each step
records the status (success, design-rule or simulation error) and the summary metrics.
"""
import copy
import math

import numpy as np

from common import SWEEP_BASELINES, baseline, evaluate_many, save

KEYS = ("pressure_ratio_total", "efficiency_isentropic", "min_stall_margin", "max_relative_inlet_mach")


def _rows(design):
    rotor = next(i for i, r in enumerate(design["rows"]) if r["row_type"] == "rotor")
    stator = next((i for i, r in enumerate(design["rows"]) if i > rotor and r["row_type"] == "stator"), None)
    return rotor, stator


def _span(design, row):
    st = design["passage"]["stations"]
    x = 0.5 * (row["leading_edge_axial_m"] + row["trailing_edge_axial_m"])
    z = [s["axial_m"] for s in st]
    return float(np.interp(x, z, [s["shroud_radius_m"] for s in st]) - np.interp(x, z, [s["hub_radius_m"] for s in st]))


def _turning_sign(row):
    return 1.0 if np.mean(np.asarray(row["metal_angle_in_deg"]) - np.asarray(row["metal_angle_out_deg"])) > 0 else -1.0


def stagger(row, delta):
    """Turn the whole section by ``delta`` deg; positive closes it (both metal angles grow in magnitude)."""
    s = np.sign(np.mean(row["metal_angle_in_deg"])) or 1.0
    row["metal_angle_in_deg"] = [a + s * delta for a in row["metal_angle_in_deg"]]
    row["metal_angle_out_deg"] = [a + s * delta for a in row["metal_angle_out_deg"]]


def camber(row, delta):
    """Add ``delta`` deg of camber at the trailing edge."""
    row["metal_angle_out_deg"] = [a - _turning_sign(row) * delta for a in row["metal_angle_out_deg"]]


def scale(key):
    def f(row, factor):
        row[key] = [v * factor for v in row[key]]
    return f


def blades(row, factor):
    row["blade_count"] = int(round(row["blade_count"] * factor))


PARAMETERS = {
    "rotor_stagger_deg": ("rotor", stagger, np.arange(-4.0, 4.01, 0.5)),
    "rotor_camber_deg": ("rotor", camber, np.arange(-4.0, 4.01, 0.5)),
    "rotor_chord_factor": ("rotor", scale("chord_m"), np.linspace(0.85, 1.15, 13)),
    "rotor_thickness_factor": ("rotor", scale("thickness_to_chord"), np.linspace(0.8, 1.2, 9)),
    "rotor_blade_factor": ("rotor", blades, np.linspace(0.8, 1.2, 9)),
    "stator_stagger_deg": ("stator", stagger, np.arange(-4.0, 4.01, 0.5)),
}
CLEARANCE_SPAN = np.linspace(0.0, 0.02, 11)
FLOW_FACTORS = np.linspace(0.90, 1.05, 31)


def jobs_for(case_id, design, task):
    jobs, labels = [], []
    rotor, stator = _rows(design)
    for name, (which, change, values) in PARAMETERS.items():
        index = rotor if which == "rotor" else stator
        if index is None:
            continue
        for v in values:
            d = copy.deepcopy(design)
            change(d["rows"][index], float(v))
            jobs.append((d, task))
            labels.append((case_id, name, float(v)))
    span = _span(design, design["rows"][rotor])
    for c in CLEARANCE_SPAN:
        d = copy.deepcopy(design)
        d["rows"][rotor]["tip_clearance_m"] = float(c * span)
        jobs.append((d, task))
        labels.append((case_id, "rotor_clearance_over_span", float(c)))
    for f in FLOW_FACTORS:
        t = copy.deepcopy(task)
        t["operating_points"][0]["mass_flow_kg_s"] *= float(f)
        jobs.append((design, t))
        labels.append((case_id, "mass_flow_factor", float(f)))
    return jobs, labels


def main():
    jobs, labels = [], []
    for case_id, speed in SWEEP_BASELINES:
        design, task = baseline(case_id, speed, solved_only=True)
        j, l = jobs_for(case_id, design, task)
        jobs += j
        labels += l
    print(len(jobs), "evaluations", flush=True)
    results = evaluate_many(jobs)
    out = {}
    for (case_id, name, value), res in zip(labels, results):
        out.setdefault(case_id, {}).setdefault(name, []).append(
            {"value": value, "status": res["status"], "error": (res["error"] or "")[:200],
             **{k: res["metrics"].get(k) for k in KEYS}})
    print(save("sweeps", out))


if __name__ == "__main__":
    main()
