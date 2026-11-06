"""Archived numerical prototype; does not modify the installed solver.

The source archive contains both the base solver and this explicit override.
Do not treat prototype results as unmodified simulator-version results.
"""
import argparse
import inspect
import sys
import textwrap
import time
import types
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from campaign import create_campaign, write_json_new
from scripts.run_throughflow import build_case
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.verification import verify_solution
import sm_throughflow.solver.throughflow as solver


class Prototype:
    def __init__(self, mode, depth, weighted):
        self.mode, self.depth, self.weighted = mode, depth, weighted
        self.history, self.trace = [], []

    def step(self, flow, t, target, geo, stations, b_star, kb_start):
        factor = flow._damping(geo, stations, b_star)
        f = factor * (target - t)
        self.trace.append(dict(iteration=len(self.trace) + 1, residual=float(np.max(np.abs(target - t))),
                               b_star=b_star, damping_min=float(factor.min()), damping_max=float(factor.max())))
        if len(self.trace) % 25 == 0:
            print(self.trace[-1], flush=True)
        x = t.ravel()
        f = f.ravel()
        if self.mode == "coupled":
            x = np.concatenate([x, kb_start])
            f = np.concatenate([f, flow._kb - kb_start])
        candidate = x + f
        if self.mode in ("anderson", "coupled"):
            self.history.append((x.copy(), f.copy()))
            self.history = self.history[-self.depth - 1:]
            if len(self.history) >= 3:
                dx = np.column_stack([b[0] - a[0] for a, b in zip(self.history, self.history[1:])])
                df = np.column_stack([b[1] - a[1] for a, b in zip(self.history, self.history[1:])])
                weights = np.concatenate([factor.ravel(), np.full(kb_start.size, .5)]) if self.mode == "coupled" else factor.ravel()
                if not self.weighted:
                    weights = np.ones_like(weights)
                gamma = np.linalg.lstsq(df / weights[:, None], f / weights, rcond=1e-10)[0]
                accelerated = candidate - (dx + df) @ gamma
                shaped = accelerated[:t.size].reshape(t.shape)
                kb_ok = self.mode != "coupled" or np.all((accelerated[t.size:] > .5) & (accelerated[t.size:] <= 1.0))
                if kb_ok and np.all(np.isfinite(shaped)) and np.max(np.abs(shaped - t)) < .03 and np.all(np.diff(shaped, axis=1) > 0):
                    candidate = accelerated
        if self.mode == "coupled":
            flow._kb = candidate[t.size:].copy()
        return candidate[:t.size].reshape(t.shape)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["novak", "fixed", "anderson", "coupled"], default="anderson")
    parser.add_argument("--subdivisions", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=250)
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--weighted", action="store_true")
    args = parser.parse_args()
    if SlcAungierSimulator.VERSION != "slc_aungier_experimental_v6":
        raise SystemExit("This v6 research override must be run from its archived source.zip; use verify_phase01.py for the current solver.")
    campaign = create_campaign(purpose="axial_iteration_prototype", selection=vars(args))
    print(campaign, flush=True)
    d, t = build_case(1)
    t["numerics"].update(duct_subdivisions=args.subdivisions)
    model, task = ThroughflowDesignV2.model_validate(d), ThroughflowTaskV2.model_validate(t)
    flow, _ = SlcAungierSimulator.build(model, task, task.operating_points[0])
    prototype = Prototype(args.mode, args.depth, args.weighted)
    # Replace only the repositioning step; retain the original equations and stopping tests.
    source = textwrap.dedent(inspect.getsource(solver.Throughflow._solve))
    original = "t = t + self._damping(geo, stations, b_star) * (t_target - t)"
    assert source.count(original) == 1
    source = source.replace(original, "t = prototype.step(self, t, t_target, geo, stations, b_star, kb_start)")
    source = source.replace("geo = surface_geometry(self.qn, t, self.curvature)", "kb_start = self._kb.copy()\n        geo = surface_geometry(self.qn, t, self.curvature)")
    if args.mode in ("fixed", "coupled"):
        source = source.replace("b_star = 0.5 * (b_star + 1.0)", "b_star = b_star")
    namespace = dict(vars(solver), prototype=prototype)
    exec(compile(source, "<archived axial-iteration prototype>", "exec"), namespace)
    flow._solve = types.MethodType(namespace["_solve"], flow)
    start = time.perf_counter()
    result = dict(prototype=True, settings=vars(args), design=d, task=task.model_dump(mode="json"))
    try:
        solution = flow._solve(1e-7, args.iterations, 16.0)
        result.update(converged=solution.convergence.converged, iterations=solution.convergence.iterations,
                      position_history=solution.convergence.position_change,
                      field_history=[v if np.isfinite(v) else None for v in solution.convergence.velocity_change])
        if solution.convergence.converged:
            result["verification"] = verify_solution(flow, solution, 1e-7)
            from sm_throughflow.solver import averaged_total_state
            a, b = [averaged_total_state(flow.gas, s) for s in (solution.stations[0], solution.stations[-1])]
            result["pressure_ratio_total"] = b[1] / a[1]
    except Exception as exc:
        result["failure"] = getattr(exc, "diagnostics", {"message": str(exc)})
    result.update(seconds=time.perf_counter() - start, trace=prototype.trace)
    write_json_new(campaign / "probe.json", result)
    print({k: v for k, v in result.items() if k not in ("trace", "design", "task", "position_history", "field_history", "verification")}, flush=True)


if __name__ == "__main__":
    main()
