"""Run validation cases and measure how consistently the simulator departs from measurement.

    python validation/run.py                 # every case, then the consistency report
    python validation/run.py nasa_stage35    # one case, then the report

Each case is solved with the environment's simulator at its measured
operating points and at the anchors of each speed line (choke, peak
efficiency, near stall). Three levels are compared (docs/validation_plan.md):

1. Overall performance, with each model quantity averaged as the report
   averages it.
2. Stage-exit profiles at the measurement plane: P0 and T0 shape, flow angle,
   meridional velocity shape.
3. Blade-element quantities of every row: incidence, deviation, loss
   coefficient, D-factor.

Per-case results go to ``validation/results/<case>.json``, and the
consistency statistics over all results to ``validation/reports/consistency.md``.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tools"))

import lewis_stage as L  # noqa: E402
from sm_throughflow.contracts import AUNGIER_PROFILES, ThroughflowDesignV2, ThroughflowTaskV2  # noqa: E402
from sm_throughflow.simulator import SlcAungierSimulator  # noqa: E402
from sm_throughflow.solver import ChokedError  # noqa: E402

RESULTS = HERE / "results"
REPORT = HERE / "reports" / "consistency.md"
CORE = (15.0, 85.0)  # percent span from the tip; the rest of the measured span is the end-wall zone
#: The highest measured flow is a choke point only where the characteristic is nearly vertical there:
#: the relative fall of PR - 1 between the two highest-flow points over their relative flow difference.
CHOKE_SLOPE = 10.0


# ------------------------------------------------------------------ cases
class LewisStage:
    """A NASA Lewis single stage: Table III geometry, overall performance, blade elements at blade edges.

    The measured tables are found by name: ``<report>_table*_overall_<NNN>pct.csv`` per speed and
    ``<report>_table*_<rotor|stator>_reading<N>.csv`` per reading (the table numbers differ between
    reports). Speed lines with fewer than three readings (near-stall points only) are skipped.
    """

    def __init__(self, case_id):
        c = L.LEWIS_STAGES[case_id]
        folder = L.CASES / case_id
        self.case_id = case_id
        self.design = L.lewis_stage_design(case_id)
        self.design_speed_rpm = 17188.7  # every report of the rig (TP-1337 Table I prints 17185.7 once for stage 37)
        self.speeds = {}
        for path in sorted(folder.glob("{}_table*_overall_*pct.csv".format(c["report"]))):
            speed = int(path.stem.rsplit("_", 1)[1][:-3])
            table = L.read_overall(path)
            if len(table) >= 3:
                self.speeds[speed] = table

        def elements(row):
            return {p.stem.rsplit("reading", 1)[1]: L.read_elements(p) for p in folder.glob("{}_table*_{}_reading*.csv".format(c["report"], row))}

        self.rotor_elements, self.stator_elements = elements(c["rotor"]), elements(c["stator"])
        geometry = L._read(folder / "{}_tableIII_{}.csv".format(c["report"], c["rotor"]))
        self.rotor_walls_in = (float(next(r for r in geometry if r["RP"] == "HUB")["RI"]), float(next(r for r in geometry if r["RP"] == "TIP")["RI"]))
        self.notes = ["tip clearance {:.2f} mm ({})".format(1e3 * c["tip_clearance_m"], c["clearance_source"]), "stator hub gap 0 (not stated)",
                      "station 3 at {:.3f} cm ({})".format(c["z_out_cm"], c["z_out_source"])]

    def inlet_blockage(self, speed):
        """The inlet-profile rule (lewis_stage.inlet_blockage), averaged over the speed line's readings
        with blade-element data, or over every reading of the case when the speed line has none."""
        readings = [r for r in self.speeds[speed] if r in self.rotor_elements] or list(self.rotor_elements)
        values = [L.inlet_blockage(self.rotor_elements[r], *self.rotor_walls_in) for r in readings]
        return float(np.mean(values)) if values else 0.02

    def measured_points(self, speed):
        points = []
        for reading, v in self.speeds[speed].items():
            points.append(dict(
                reading=reading, mass_flow=v["AIRFLOW AT ORIFICE"], rpm=v["ROTATIVE SPEED"],
                stage_pr=v["STAGE TOTAL PRESSURE RATIO"], stage_tr=v["STAGE TOTAL TEMPERATURE RATIO"], stage_eta=v["STAGE ADIABATIC EFFICIENCY"],
                rotor_pr=v["ROTOR TOTAL PRESSURE RATIO"], rotor_tr=v["ROTOR TOTAL TEMPERATURE RATIO"], rotor_eta=v["ROTOR ADIABATIC EFFICIENCY"],
            ))
        return points


CASES = {case_id: (lambda c=case_id: LewisStage(c)) for case_id in L.LEWIS_STAGES}


# ------------------------------------------------------------------ model
class Solution:
    """One converged operating point, with every quantity the comparison needs."""

    def __init__(self, design, mass_flow, rpm, blockage):
        task = ThroughflowTaskV2.model_validate(L.task([("p", mass_flow, rpm)], inlet_blockage=blockage))
        model = ThroughflowDesignV2.model_validate(design)
        flow, rows = SlcAungierSimulator.build(model, task, task.operating_points[0])
        sol = flow.solve(tol=task.numerics.tolerance, max_iterations=task.numerics.max_iterations, b_star=16.0)
        if not sol.convergence.converged:
            raise RuntimeError("did not converge")
        self.mass_flow, self.rpm = mass_flow, rpm
        self.omega = rpm * 2.0 * math.pi / 60.0
        self.gas, self.sol, self.design = flow.gas, sol, model
        self.k = (self.gas.gamma - 1.0) / self.gas.gamma
        s = sol.stations
        self.inlet, self.rotor_in, self.rotor_out, self.stator_in, self.stator_out, self.exit = s[0], s[1], s[2], s[3], s[4], s[-1]
        tr = self._ratio(self.rotor_out, "T0")
        self.overall = dict(
            rotor_pr=self._energy_ratio(self.rotor_out), rotor_tr=tr,
            stage_pr=self._energy_ratio(self.exit), stage_tr=self._ratio(self.exit, "T0"),
        )
        self.overall["rotor_eta"] = (self.overall["rotor_pr"] ** self.k - 1.0) / (tr - 1.0)
        self.overall["stage_eta"] = (self.overall["stage_pr"] ** self.k - 1.0) / (tr - 1.0)  # TP-1338 (B14)
        self.min_stall_margin = min(
            float(np.nanmin(d["equivalent_velocity_ratio"] / d["stall_velocity_ratio"] - 1.0))
            for d in (sol.performance[r.row_id].diagnostics for r in model.rows))

    def _ratio(self, station, name):
        """Mass average of a total-quantity ratio to the inlet value on the same stream surface (B12)."""
        return float(station.mass_average(getattr(station, name) / getattr(self.inlet, name)))

    def _energy_ratio(self, station):
        """Energy-averaged total-pressure ratio: mass average of (P0/P01)^k, then the 1/k power (B10, B11)."""
        return float(station.mass_average((station.P0 / self.inlet.P0) ** self.k) ** (1.0 / self.k))

    @staticmethod
    def _span(station):
        return 100.0 * (1.0 - np.asarray(station.t))  # percent span from the tip

    def row_profiles(self, row_id, inlet, exit):
        """Blade-element quantities of a row against percent span from the tip at its exit."""
        d = self.sol.performance[row_id].diagnostics
        frame = self.omega if row_id.startswith("R") else 0.0
        w1 = np.hypot(inlet.Wm, inlet.C_theta - frame * inlet.r)
        w2 = np.hypot(exit.Wm, exit.C_theta - frame * exit.r)
        circulation = np.abs(exit.r * exit.C_theta - inlet.r * inlet.C_theta)
        d_factor = 1.0 - w2 / w1 + circulation / ((inlet.r + exit.r) * np.asarray(d["solidity"]) * w1)  # Lieblein, as the reports
        return self._span(exit), dict(incidence=np.asarray(d["incidence"]), deviation=np.asarray(d["deviation"]),
                                      loss=np.asarray(d["loss"]), d_factor=d_factor)

    def exit_profiles(self):
        st = self.exit
        return self._span(st), dict(p0_ratio=np.asarray(st.P0 / self.inlet.P0), t0_ratio=np.asarray(st.T0 / self.inlet.T0),
                                    angle=np.degrees(np.asarray(st.alpha)), vm=np.asarray(st.Wm), r=np.asarray(st.r))


def solve(design, mass_flow, rpm, blockage):
    try:
        return Solution(design, mass_flow, rpm, blockage)
    except (ChokedError, RuntimeError, ValueError, FloatingPointError):
        return None


def choke_flow(design, rpm, blockage, start, tol=1e-3):
    """Largest mass flow the model passes at a speed, by bisection from a converged ``start``."""
    lo, hi = start, start * 1.02
    while solve(design, hi, rpm, blockage) is not None:
        lo, hi = hi, hi * 1.02
    while (hi - lo) / lo > tol:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if solve(design, mid, rpm, blockage) is not None else (lo, mid)
    return lo


def speed_line(design, rpm, blockage, m_choke, lowest=0.75, count=16):
    """The model's characteristic from just below choke down to ``lowest`` of the choke flow."""
    out = []
    for m in np.linspace(m_choke * 0.999, m_choke * lowest, count):
        s = solve(design, float(m), rpm, blockage)
        if s is None:
            out.append(dict(mass_flow=float(m), converged=False))
            continue
        out.append(dict(mass_flow=float(m), converged=True, min_stall_margin=s.min_stall_margin, **s.overall))
    return out


def model_anchors(line):
    ok = [p for p in line if p["converged"]]
    peak = max(ok, key=lambda p: p["stage_eta"])
    i = ok.index(peak)
    if 0 < i < len(ok) - 1:  # parabola through the three points around the maximum
        m = np.array([ok[j]["mass_flow"] for j in (i - 1, i, i + 1)])
        e = np.array([ok[j]["stage_eta"] for j in (i - 1, i, i + 1)])
        a, b, c = np.polyfit(m, e, 2)
        if a < 0:
            m_peak = -b / (2 * a)
            peak = dict(peak, mass_flow=float(m_peak), stage_eta=float(np.polyval([a, b, c], m_peak)),
                        stage_pr=float(np.interp(m_peak, m[::-1], [ok[j]["stage_pr"] for j in (i + 1, i, i - 1)])))
    stall = None
    for a_, b_ in zip(ok, ok[1:]):
        if a_["min_stall_margin"] >= 0.0 > b_["min_stall_margin"]:
            f = a_["min_stall_margin"] / (a_["min_stall_margin"] - b_["min_stall_margin"])
            stall = {k: a_[k] + f * (b_[k] - a_[k]) for k in ("mass_flow", "stage_pr", "stage_eta")}
            break
    return peak, stall


# ------------------------------------------------------------------ comparison
def errors(model, meas):
    """Errors in forms that compare across machines (docs/validation_plan.md, section 2)."""
    out = {}
    for key in ("stage_pr", "rotor_pr"):
        out[key + "_rise"] = (model[key] - 1.0) / (meas[key] - 1.0) - 1.0
    for key in ("stage_tr", "rotor_tr"):
        out[key + "_rise"] = (model[key] - 1.0) / (meas[key] - 1.0) - 1.0
    for key in ("stage_eta", "rotor_eta"):
        out[key + "_points"] = 100.0 * (model[key] - meas[key])
    return out


def _weights(r, vm):
    return np.asarray(r) * np.asarray(vm)


def _shape(values, base, weights):
    values = np.asarray(values, dtype=float)
    avg = float(np.sum(weights * values) / np.sum(weights))
    return (values - avg) / (avg - base)


#: Percent span from the tip of the Lewis blade-element rows RP 1 to 9.
RP_SPAN = {1: 5.0, 2: 10.0, 3: 15.0, 4: 30.0, 5: 50.0, 6: 70.0, 7: 85.0, 8: 90.0, 9: 95.0}
LEVEL2_COLUMNS = ("TOTAL PRESS IN", "TOTAL PRESS RATIO", "TOTAL TEMP IN", "TOTAL TEMP RATIO", "MERID VEL OUT", "RADII OUT", "ABS BETAM OUT")


def compare_profiles(sol, rotor_rows, stator_rows):
    """Levels 2 and 3 at the measured spans; the model is interpolated to them.

    A row whose cells a report left unprinted is skipped for the quantities it lacks.
    """
    rotor_rows = [dict(r, **{"PERCENT SPAN": RP_SPAN[int(r["RP"])]}) for r in rotor_rows]
    stator_rows = [dict(r, **{"PERCENT SPAN": RP_SPAN[int(r["RP"])]}) for r in stator_rows]
    full = [r for r in stator_rows if all(c in r for c in LEVEL2_COLUMNS)]
    stator_level2, stator_rows_all = full, stator_rows
    stator_rows = stator_level2
    spans = np.array([r["PERCENT SPAN"] for r in stator_rows])
    span_m, ex = sol.exit_profiles()
    order = np.argsort(span_m)

    def at(values, where=spans, span=span_m, o=order):
        return np.interp(where, span[o], np.asarray(values)[o])

    meas_p = np.array([r["TOTAL PRESS IN"] * r["TOTAL PRESS RATIO"] for r in stator_rows]) / 10.1325
    meas_t = np.array([r["TOTAL TEMP IN"] * r["TOTAL TEMP RATIO"] for r in stator_rows]) / 288.15
    meas_vm = np.array([r["MERID VEL OUT"] for r in stator_rows])
    radius = np.array([r["RADII OUT"] for r in stator_rows])
    w = _weights(radius, meas_vm)
    model_p, model_t, model_vm = at(ex["p0_ratio"]), at(ex["t0_ratio"]), at(ex["vm"])
    level2 = dict(
        span=spans.tolist(),
        p0_shape=dict(measured=_shape(meas_p, 1.0, w).tolist(), model=_shape(model_p, 1.0, w).tolist()),
        t0_shape=dict(measured=_shape(meas_t, 1.0, w).tolist(), model=_shape(model_t, 1.0, w).tolist()),
        angle=dict(measured=[r["ABS BETAM OUT"] for r in stator_rows], model=at(ex["angle"]).tolist()),
        vm_shape=dict(measured=(meas_vm / np.sum(w * meas_vm) * np.sum(w) - 1.0).tolist(),
                      model=(model_vm / np.sum(w * model_vm) * np.sum(w) - 1.0).tolist()),
    )
    level3 = {}
    for row_id, rows, inlet, exit in (("R1", rotor_rows, sol.rotor_in, sol.rotor_out), ("S1", stator_rows_all, sol.stator_in, sol.stator_out)):
        span_r, q = sol.row_profiles(row_id, inlet, exit)
        o = np.argsort(span_r)
        level3[row_id] = {}
        for key, column in (("incidence", "INCIDENCE MEAN"), ("deviation", "DEV"), ("loss", "LOSS COEFF TOT"), ("d_factor", "D FACT")):
            have = [r for r in rows if column in r]
            where = np.array([r["PERCENT SPAN"] for r in have])
            level3[row_id][key] = dict(span=where.tolist(), measured=[r[column] for r in have], model=np.interp(where, span_r[o], q[key][o]).tolist())
    return level2, level3


def run_case(case_id):
    case = CASES[case_id]()
    if not case.speeds:
        print("  no measured speed lines transcribed; skipped")
        return None
    result = dict(case=case_id, simulator=SlcAungierSimulator.VERSION, physics=AUNGIER_PROFILES["axial_compressor_aungier_v1"],
                  assumptions=list(L.ASSUMPTIONS) + case.notes, speeds={})
    for speed in case.speeds:
        blockage = case.inlet_blockage(speed)
        points = case.measured_points(speed)
        rpm = case.design_speed_rpm * speed / 100.0
        by_flow = sorted(points, key=lambda p: -p["mass_flow"])
        meas_choke = by_flow[0]
        fall = (by_flow[1]["stage_pr"] - meas_choke["stage_pr"]) / (meas_choke["stage_pr"] - 1.0)
        spread = 1.0 - by_flow[1]["mass_flow"] / meas_choke["mass_flow"]
        slope = fall / spread if spread > 0.0 else (math.inf if fall > 0.0 else 0.0)  # equal flows, PR falling: vertical
        choked = slope >= CHOKE_SLOPE
        meas_peak = max(points, key=lambda p: p["stage_eta"])
        meas_stall = min(points, key=lambda p: p["mass_flow"])
        start = next((p["mass_flow"] for p in sorted(points, key=lambda p: p["mass_flow"]) if solve(case.design, p["mass_flow"], rpm, blockage)), None)
        m = min(p["mass_flow"] for p in points)
        while start is None and m > 0.5 * meas_choke["mass_flow"]:  # the model chokes below every measured flow
            m *= 0.97
            start = m if solve(case.design, m, rpm, blockage) else None
        if start is None:
            result["speeds"][str(speed)] = dict(rpm=rpm, inlet_blockage=blockage, failed="no converged point down to half the measured flow")
            continue
        m_choke = choke_flow(case.design, rpm, blockage, start)
        line = speed_line(case.design, rpm, blockage, m_choke)
        peak, stall = model_anchors(line)
        anchors = dict(
            choke=dict(measured=meas_choke["mass_flow"], model=m_choke, measured_is_choke=choked, measured_slope=slope,
                       error=m_choke / meas_choke["mass_flow"] - 1.0 if choked else None),
            peak=dict(measured={k: meas_peak[k] for k in ("mass_flow", "stage_pr", "stage_eta")}, model={k: peak[k] for k in ("mass_flow", "stage_pr", "stage_eta")},
                      error=dict(mass_flow=peak["mass_flow"] / meas_peak["mass_flow"] - 1.0,
                                 stage_pr_rise=(peak["stage_pr"] - 1.0) / (meas_peak["stage_pr"] - 1.0) - 1.0,
                                 stage_eta_points=100.0 * (peak["stage_eta"] - meas_peak["stage_eta"]))),
            stall=dict(measured={k: meas_stall[k] for k in ("mass_flow", "stage_pr", "stage_eta")}, model=stall,
                       error=None if stall is None else dict(mass_flow=stall["mass_flow"] / meas_stall["mass_flow"] - 1.0)),
        )
        if stall is not None:
            sm = lambda s, p: 100.0 * ((s["stage_pr"] / p["stage_pr"]) * (p["mass_flow"] / s["mass_flow"]) - 1.0)  # (B23)
            anchors["stall"]["stall_margin"] = dict(measured_last_stable=sm(meas_stall, meas_peak), model=sm(stall, peak))
        readings = []
        for p in points:
            entry = dict(reading=p["reading"], measured=p)
            matched = [("at_matched_flow", p["mass_flow"] * m_choke / meas_choke["mass_flow"])] if choked else []
            for label, m in [("at_measured_flow", p["mass_flow"])] + matched:
                sol = solve(case.design, m, p["rpm"], blockage)
                if sol is None:
                    entry[label] = dict(mass_flow=m, converged=False)
                    continue
                block = dict(mass_flow=m, converged=True, overall=sol.overall, errors=errors(sol.overall, p), min_stall_margin=sol.min_stall_margin)
                if p["reading"] in case.rotor_elements:
                    block["level2"], block["level3"] = compare_profiles(sol, case.rotor_elements[p["reading"]], case.stator_elements[p["reading"]])
                entry[label] = block
            readings.append(entry)
        result["speeds"][str(speed)] = dict(rpm=rpm, inlet_blockage=blockage, anchors=anchors, speed_line=line, readings=readings)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / (case_id + ".json")).write_text(json.dumps(result, indent=1, default=float) + "\n")
    return result


# ------------------------------------------------------------------ report
def _zone(span):
    return "core" if CORE[0] <= span <= CORE[1] else "end-wall"


def _stats(values):
    v = np.asarray([x for x in values if x is not None and np.isfinite(x)], dtype=float)
    if v.size == 0:
        return "n/a"
    return "{:+.3f} / {:.3f} (n={})".format(v.mean(), v.std(ddof=1) if v.size > 1 else float("nan"), v.size)


def report(results):
    lines = ["# Validation consistency report", "",
             "Generated by `validation/run.py`. Bias / spread are the mean / sample standard deviation of",
             "the error over the cases and points listed; the spread is what docs/validation_plan.md gates.", ""]
    lines += ["Simulator: " + ", ".join(sorted({r["simulator"] for r in results})), ""]
    overall, anchor_rows, profile = {}, [], {}
    for r in results:
        for speed, s in r["speeds"].items():
            if "failed" in s:
                anchor_rows.append("| {} | {} | {:.3f} | {} | | | | |".format(r["case"], speed, s["inlet_blockage"], s["failed"]))
                continue
            a = s["anchors"]
            choke = ("{:+.2%}".format(a["choke"]["error"]) if a["choke"].get("measured_is_choke", True)
                     else "not choked ({:+.2%} vs max. flow)".format(a["choke"]["model"] / a["choke"]["measured"] - 1.0))
            anchor_rows.append("| {} | {} | {:.3f} | {} | {:+.2%} | {:+.2%} | {:+.1f} | {} |".format(
                r["case"], speed, s["inlet_blockage"], choke, a["peak"]["error"]["mass_flow"], a["peak"]["error"]["stage_pr_rise"],
                a["peak"]["error"]["stage_eta_points"],
                "none found" if a["stall"]["model"] is None else "{:+.1%}".format(a["stall"]["error"]["mass_flow"])))
            for p in s["readings"]:
                for label in ("at_measured_flow", "at_matched_flow"):
                    b = p.get(label, {})
                    if not b.get("converged"):
                        continue
                    for key, value in b["errors"].items():
                        overall.setdefault((label, key), []).append(value)
                    for level in ("level2", "level3"):
                        if level not in b:
                            continue
                        blocks = {"exit": b["level2"]} if level == "level2" else b["level3"]
                        for where, data in blocks.items():
                            for key, pair in data.items():
                                if key == "span":
                                    continue
                                spans = pair.get("span", data.get("span"))
                                for span, mo, me in zip(spans, pair["model"], pair["measured"]):
                                    profile.setdefault((label, where, key, _zone(span)), []).append(mo - me)
    lines += ["## Anchors", "", "| Case | Speed % | Inlet blockage | Choke flow | Peak-eff. flow | Peak PR rise | Peak eff. (pts) | Stall flow |",
              "|---|---|---|---|---|---|---|---|"] + anchor_rows + [""]
    unreached = ["{} {}% {}".format(r["case"], sp, p["reading"]) for r in results for sp, s in r["speeds"].items() if "readings" in s
                 for p in s["readings"] if not p["at_measured_flow"]["converged"]]
    lines += ["Measured points the model cannot reach (it chokes or fails below their flow): " + (", ".join(unreached) or "none"), ""]
    lines += ["## Overall errors at every measured point", "", "Bias / spread (n). Rises are relative errors of PR - 1 and TR - 1; efficiencies in points.", "",
              "| Error | At measured flow | At matched flow (m/m_choke) |", "|---|---|---|"]
    for key in sorted({k for _, k in overall}):
        lines.append("| {} | {} | {} |".format(key, _stats(overall.get(("at_measured_flow", key), [])), _stats(overall.get(("at_matched_flow", key), []))))
    lines += ["", "## Profile errors (model - measured)", "",
              "Bias / spread (n) over every measured span and point. Shapes: P0 and T0 as (X - X_avg)/(X_avg - X_in),",
              "Vm as Vm/Vm_avg - 1; angles, incidence and deviation in degrees.", "",
              "| Where | Quantity | Zone | At measured flow | At matched flow |", "|---|---|---|---|---|"]
    for where, key, zone in sorted({k[1:] for k in profile}):
        lines.append("| {} | {} | {} | {} | {} |".format(where, key, zone, _stats(profile.get(("at_measured_flow", where, key, zone), [])),
                                                       _stats(profile.get(("at_matched_flow", where, key, zone), []))))
    lines += ["", "## Assumptions per case", ""]
    for r in results:
        lines += ["- **{}**: {}".format(r["case"], "; ".join(r["assumptions"]))]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")


def _run_logged(case_id):
    import traceback
    try:
        run_case(case_id)
        return case_id, None
    except Exception:
        return case_id, traceback.format_exc()


def main(argv):
    from concurrent.futures import ProcessPoolExecutor

    ids = argv or list(CASES)
    with ProcessPoolExecutor(max_workers=min(len(ids), 4)) as pool:
        for case_id, error in pool.map(_run_logged, ids):
            print(case_id, "done" if error is None else "FAILED" + chr(10) + error, flush=True)
    results = [json.loads(p.read_text()) for p in sorted(RESULTS.glob("*.json"))]
    report(results)
    print("wrote", REPORT)


if __name__ == "__main__":
    main(sys.argv[1:])
