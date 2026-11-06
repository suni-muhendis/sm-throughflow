"""Study 3: conservation on every stream surface of the full model (losses, end walls, leakage on).

For each baseline at three flows (the measured design reading, and 3 percent above and below it),
the converged solution is checked station by station:
- mass: every station carries the task's mass flow, every stream tube its equal share;
- energy: across a rotor, H2 - H1 = omega (r2 C_theta2 - r1 C_theta1) on each stream surface (Euler);
  across a stator or a duct, H is unchanged on each stream surface;
- second law: entropy never falls along a stream surface;
- the overall power from the mass-averaged total temperature equals the sum over stream tubes.
"""
import copy
import warnings

import numpy as np

from common import BASELINES, baseline, save
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator


def check(design, task):
    model = ThroughflowDesignV2.model_validate(design)
    t = ThroughflowTaskV2.model_validate(task)
    point = t.operating_points[0]
    flow, rows = SlcAungierSimulator.build(model, t, point)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sol = flow.solve(tol=t.numerics.tolerance, max_iterations=t.numerics.max_iterations, b_star=16.0)
    if not sol.convergence.converged:
        return {"converged": False}
    st = sol.stations
    m = point.mass_flow_kg_s
    n = len(st[0].r) - 1
    out = {"converged": True}
    out["mass_rel_error_max"] = float(max(abs(s.mass_flow / m - 1.0) for s in st))
    out["tube_share_error_max"] = float(max(np.max(np.abs(s.tube_mass_flows / m - 1.0 / n)) for s in st))
    euler, h_jump, ds_min = 0.0, 0.0, np.inf
    omega = point.shaft_speed_rpm * 2.0 * np.pi / 60.0
    for k in range(len(st) - 1):
        a, b = st[k], st[k + 1]
        solver_row = flow.row_at.get(k)
        row = next((r for r in model.rows if solver_row is not None and r.row_id == solver_row.name), None)
        if row is not None and row.row_type == "rotor":
            work = omega * (b.r * b.C_theta - a.r * a.C_theta)
            euler = max(euler, float(np.max(np.abs((b.H - a.H) - work) / np.maximum(np.abs(work), 1.0))))
        else:
            h_jump = max(h_jump, float(np.max(np.abs(b.H - a.H) / a.H)))
        ds_min = min(ds_min, float(np.min(b.s - a.s)))
    out["euler_rel_error_max"] = euler
    out["stator_duct_H_rel_change_max"] = h_jump
    out["entropy_change_min_J_kgK"] = ds_min
    first, last = st[0], st[-1]
    tubes = 0.5 * (last.H[1:] + last.H[:-1]) - 0.5 * (first.H[1:] + first.H[:-1])
    power_tubes = float(np.sum(last.tube_mass_flows * tubes))
    power_avg = m * (last.mass_average(last.H) - first.mass_average(first.H))
    out["power_tube_vs_average_rel"] = abs(power_tubes / power_avg - 1.0)
    return out


def main():
    out = {}
    for case_id, speed in BASELINES:
        design, task = baseline(case_id, speed)
        for label, f in (("design", 1.0), ("plus3", 1.03), ("minus3", 0.97)):
            t = copy.deepcopy(task)
            t["operating_points"][0]["mass_flow_kg_s"] *= f
            try:
                out.setdefault(case_id, {})[label] = check(design, t)
            except Exception as exc:  # report, do not hide
                out.setdefault(case_id, {})[label] = {"converged": False, "error": "{}: {}".format(type(exc).__name__, exc)}
            out[case_id][label]["design"] = design
            out[case_id][label]["task"] = ThroughflowTaskV2.model_validate(t).model_dump(mode="json")
            print(case_id, label, {k: v for k, v in out[case_id][label].items() if k not in ("design", "task")}, flush=True)
    print(save("conservation", out))


if __name__ == "__main__":
    main()
