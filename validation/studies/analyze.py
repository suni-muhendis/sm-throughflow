"""Analyze one explicit campaign without overwriting historical reports."""
import json
import sys
from pathlib import Path
from collections import Counter

import numpy as np

from common import RESULTS, VALIDATION

REPORT = None


def load(name):
    path = RESULTS / (name + ".json")
    return json.loads(path.read_text()) if path.exists() else None


def holes(statuses):
    """Failed steps with a success on both sides, and failed steps beyond the solved range."""
    ok = [s == "success" for s in statuses]
    if not any(ok):
        return 0, len(ok)
    first, last = ok.index(True), len(ok) - 1 - ok[::-1].index(True)
    inner = sum(1 for k in range(first, last + 1) if not ok[k])
    return inner, len(ok) - (last - first + 1)


def fmt(v, f="{:.4f}"):
    return "-" if v is None else f.format(v)


def admission(lines):
    d = load("admission")
    if not d:
        return
    lines += ["## Admission: the validation designs through the environment", "",
              "Each case's design at its measured design-speed readings (two-stage fan R67: 90 percent).", "",
              "| Case | Design rules | Readings solved |", "|---|---|---|"]
    for case, pts in d["points"].items():
        ok = sum(p["status"] == "success" for p in pts)
        lines.append("| {} | {} | {} of {} |".format(case, d["drc"][case] or "pass", ok, len(pts)))
    lines.append("")


def numerics(lines):
    d = load("numerics")
    if not d:
        return
    lines += ["## Determinism", "", "| Case | Status | Same process | Separate processes |", "|---|---|---|---|"]
    for case, v in d["determinism"].items():
        lines.append("| {} | {} | {} | {} |".format(case, v.get("status", ""), "identical" if v["same_process_identical"] else "DIFFERENT",
                                                   "identical" if v.get("cross_process_identical") else "DIFFERENT"))
    lines += ["", "## Numerical settings", "",
              "Pressure ratio / isentropic efficiency for one setting changed at a time (default: 11 stream surfaces, "
              "tolerance 1e-7, full curvature). `x` = no converged solution, `D` = rejected by the design rules.", ""]
    for kind in ("stream_surfaces", "tolerance", "curvature"):
        values = None
        rows = []
        for case, v in d["numerics"].items():
            entries = v.get(kind, [])
            values = [e["value"] for e in entries]
            cells = []
            for e in entries:
                if e["status"] == "success":
                    cells.append("{:.4f} / {:.4f}".format(e["pressure_ratio_total"], e["efficiency_isentropic"]))
                else:
                    cells.append("D" if e["status"] == "drc_error" else "x")
            rows.append("| {} | {} |".format(case, " | ".join(cells)))
        lines += ["| Case | " + " | ".join("{} = {}".format(kind, v) for v in values) + " |", "|---|" + "---|" * len(values)] + rows + [""]


def conservation(lines):
    d = load("conservation")
    if not d:
        return
    keys = ("mass_rel_error_max", "tube_share_error_max", "euler_rel_error_max", "stator_duct_H_rel_change_max",
            "entropy_change_min_J_kgK", "power_tube_vs_average_rel")
    worst = {k: 0.0 for k in keys}
    worst["entropy_change_min_J_kgK"] = np.inf
    solved, failed = 0, []
    for case, pts in d.items():
        for label, r in pts.items():
            if not r.get("converged"):
                failed.append("{} {}".format(case, label))
                continue
            solved += 1
            for k in keys:
                worst[k] = min(worst[k], r[k]) if k == "entropy_change_min_J_kgK" else max(worst[k], r[k])
    lines += ["## Conservation on every stream surface", "",
              "Worst value over {} converged solutions (each baseline at its design reading and at +/- 3 percent flow).".format(solved), "",
              "| Check | Worst |", "|---|---|"]
    names = {"mass_rel_error_max": "Mass flow at a station, relative error", "tube_share_error_max": "Stream-tube share of the mass flow, error",
             "euler_rel_error_max": "Rotor work against Euler, relative error", "stator_duct_H_rel_change_max": "Total enthalpy change across a stator or duct, relative",
             "entropy_change_min_J_kgK": "Smallest entropy change along a stream surface, J/(kg K)",
             "power_tube_vs_average_rel": "Power from stream tubes against the mass average, relative"}
    for k in keys:
        lines.append("| {} | {:.2e} |".format(names[k], worst[k]))
    lines += ["", "No converged solution: " + (", ".join(failed) or "none"), ""]


def sweeps(lines):
    d = load("sweeps")
    if not d:
        return
    totals = Counter()
    rows = []
    for case, params in d.items():
        for name, steps in params.items():
            st = [s["status"] for s in steps]
            inner, ends = holes(st)
            e = [s["efficiency_isentropic"] for s in steps if s["status"] == "success"]
            direction = ""
            if name == "rotor_clearance_over_span" and len(e) > 2:
                direction = "falls" if all(b <= a + 1e-9 for a, b in zip(e, e[1:])) else "NOT monotone"
                totals["clearance_monotone"] += direction == "falls"
                totals["clearance_sweeps"] += 1
            if inner or direction:
                rows.append("| {} | {} | {} | {} | {} | {} | {} |".format(case, name, len(st), inner, ends,
                                                                          "{:.3f} to {:.3f}".format(min(e), max(e)) if e else "-", direction))
            totals["steps"] += len(st)
            totals["holes"] += inner
            totals["ends"] += ends
            totals["sweeps"] += 1
            totals["sweeps_with_holes"] += inner > 0
            totals.update(Counter(st))
    lines += ["## One-parameter sweeps", "",
              "{steps} evaluations in {sweeps} sweeps: {success} solved, {simulation_error} without a converged solution, "
              "{drc_error} rejected by the design rules, {schema} rejected by the schema. Holes (a failed step with solved steps on "
              "both sides): {holes} in {sweeps_with_holes} sweeps. Efficiency falls monotonically with tip clearance in "
              "{clearance_monotone} of {clearance_sweeps} designs.".format(schema=totals.get("schema_error", 0), **{k: totals.get(k, 0) for k in (
                  "steps", "sweeps", "success", "simulation_error", "drc_error", "holes", "sweeps_with_holes", "clearance_monotone", "clearance_sweeps")}), "",
              "Sweeps with holes, and every clearance sweep:", "",
              "| Case | Parameter | Steps | Holes | Failed beyond the solved range | Efficiency range | Clearance trend |",
              "|---|---|---|---|---|---|---|"] + rows + [""]


def robustness(lines):
    d = load("robustness")
    if not d:
        return
    c, msgs, rows = Counter(), Counter(), []
    for case, samples in d.items():
        cc = Counter(s["status"] for s in samples)
        c.update(cc)
        rows.append("| {} | {} | {} | {} | {} |".format(case, len(samples), cc.get("success", 0), cc.get("drc_error", 0) + cc.get("schema_error", 0),
                                                        cc.get("simulation_error", 0)))
        for s in samples:
            if s["status"] == "simulation_error":
                m = s["error"]
                key = ("choked quasi-normal" if "cannot pass" in m or "chokes" in m else
                       "no hub meridional velocity" if "no hub meridional" in m else
                       "not converged in the iteration limit" if "did not converge" in m else m[-60:])
                msgs[key] += 1
            elif s["status"] in ("drc_error", "schema_error"):
                msgs["rule: " + s["error"].split(" ", 4)[-1][:70]] += 1
    lines += ["## Random designs near each baseline", "",
              "Every row perturbed at once (stagger and camber +/- 3 deg, chord +/- 10 %, t/c +/- 15 % as smooth spanwise "
              "distributions, blade count +/- 15 %, clearance +/- 1 % of span), at the baseline's operating point.", "",
              "| Baseline | Designs | Solved | Rejected by the rules | No converged solution |", "|---|---|---|---|---|"] + rows
    lines += ["", "Reasons: " + "; ".join("{} ({})".format(m, n) for m, n in msgs.most_common()), ""]
    etas = [s["efficiency_isentropic"] for v in d.values() for s in v if s["efficiency_isentropic"] is not None]
    if etas:
        lines += ["Isentropic efficiency of the solved designs: {:.3f} to {:.3f} (median {:.3f}).".format(min(etas), max(etas), float(np.median(etas))), ""]


def search(lines):
    d = load("search")
    if not d:
        return
    lines += ["## Efficiency search", "", "A (1+6) evolution strategy over whole-design perturbations, 12 generations, maximizing isentropic efficiency.", "",
              "| Start | Efficiency, baseline -> best | Pressure ratio | Min. stall margin | Max. loss coefficient | Max. D_eq |",
              "|---|---|---|---|---|---|"]
    for case, v in d.items():
        b, e = v["baseline"], v["best"]
        lines.append("| {} | {} -> {} | {} -> {} | {} -> {} | {} -> {} | {} -> {} |".format(
            case, fmt(b["efficiency_isentropic"]), fmt(e["efficiency_isentropic"]), fmt(b["pressure_ratio_total"]), fmt(e["pressure_ratio_total"]),
            fmt(b["min_stall_margin"], "{:.3f}"), fmt(e["min_stall_margin"], "{:.3f}"), fmt(b["max_loss_coefficient"], "{:.3f}"),
            fmt(e["max_loss_coefficient"], "{:.3f}"), fmt(b["max_equivalent_diffusion"], "{:.2f}"), fmt(e["max_equivalent_diffusion"], "{:.2f}")))
    lines.append("")


def main():
    global RESULTS, REPORT
    if len(sys.argv) > 1:
        campaign = Path(sys.argv[1]).resolve()
    elif RESULTS is not None:
        campaign = RESULTS.parent
    else:
        raise ValueError("supply a campaign directory or run through run_all.py")
    if not (campaign / "manifest.json").is_file():
        raise ValueError("campaign manifest is required")
    RESULTS = campaign / "results"
    REPORT = campaign / "internal_consistency.md"
    lines = ["# Internal-consistency studies", "",
             "Generated from this campaign only; see its manifest and results for provenance.", ""]
    for part in (admission, numerics, conservation, sweeps, robustness, search):
        part(lines)
    with REPORT.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")
    print(REPORT)


if __name__ == "__main__":
    main()
