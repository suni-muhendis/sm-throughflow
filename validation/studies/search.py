"""Study 6: what does a naive optimizer find when it maximizes efficiency?

A (1+6) evolution strategy perturbs whole designs (perturb.py) from four baselines and keeps the
child of highest isentropic efficiency, with no constraint but the environment's own (schema,
design rules, a converged solution). Whatever it finds is what a learner rewarded on efficiency
would drift towards: the study records the best designs' metrics and how they differ from the
baseline, to see whether the gain is physical or an artefact of the model.
"""
import copy

import numpy as np

from common import baseline, evaluate, evaluate_many, save
from perturb import perturb

STARTS = [("nasa_stage35", 100), ("nasa_stage52", 100), ("nasa_stage6_1", 100), ("nasa_stage66_igv", 100)]
GENERATIONS, CHILDREN, STEP = 12, 6, 0.5
KEYS = ("pressure_ratio_total", "efficiency_isentropic", "efficiency_polytropic", "min_stall_margin", "max_relative_inlet_mach",
        "max_loss_coefficient", "max_equivalent_diffusion", "power_W")


def add(vec, draw, step):
    out = []
    for a, b in zip(vec, draw):
        out.append({k: (np.asarray(a[k]) + step * np.asarray(b[k])) for k in a})
    return out


def zero(vec):
    return [{k: np.zeros_like(np.asarray(v[k], dtype=float)) for k in v} for v in vec]


def main():
    rng = np.random.default_rng(7)
    out = {}
    for case_id, speed in STARTS:
        design, task = baseline(case_id, speed, solved_only=True)
        _, template = perturb(design, rng)
        best_vec = zero(template)
        base = evaluate(design, task)
        best = base["metrics"].get("efficiency_isentropic", -1.0)
        history = [{"generation": 0, "efficiency_isentropic": best}]
        best_metrics = base["metrics"]
        for g in range(1, GENERATIONS + 1):
            vecs, jobs = [], []
            for _ in range(CHILDREN):
                _, draw = perturb(design, rng)
                v = add(best_vec, draw, STEP)
                d, _ = perturb(design, rng, vector=v)
                vecs.append(v)
                jobs.append((d, task))
            results = evaluate_many(jobs)
            statuses = [r["status"] for r in results]
            for v, r in zip(vecs, results):
                e = r["metrics"].get("efficiency_isentropic")
                if r["status"] == "success" and e is not None and e > best:
                    best, best_vec, best_metrics = e, v, r["metrics"]
            history.append({"generation": g, "efficiency_isentropic": best, "statuses": statuses})
            print(case_id, g, round(best, 4), statuses, flush=True)
        change = [{k: (float(np.mean(np.abs(v[k]))) if np.ndim(v[k]) else float(v[k])) for k in v} for v in best_vec]
        out[case_id] = {"baseline": {k: base["metrics"].get(k) for k in KEYS}, "best": {k: best_metrics.get(k) for k in KEYS},
                        "history": history, "mean_abs_change_per_row": change}
    print(save("search", out))


if __name__ == "__main__":
    main()
