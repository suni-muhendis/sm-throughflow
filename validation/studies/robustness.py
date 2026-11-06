"""Study 5: how often do nearby random designs pass the rules and solve, and how do they fail?

Around each sweep baseline, ``SAMPLES`` designs are drawn with every row perturbed at once
(perturb.py, unit amplitude), at the baseline's operating point. Outcomes are counted by stage
(schema, design rule, simulation, success), simulation failures by message, and successful
designs are screened for values a physical compressor cannot reach.
"""
import numpy as np

from common import SWEEP_BASELINES, baseline, evaluate_many, save
from perturb import perturb

SAMPLES = 40
KEYS = ("pressure_ratio_total", "efficiency_isentropic", "efficiency_polytropic", "min_stall_margin", "max_relative_inlet_mach",
        "max_loss_coefficient", "max_equivalent_diffusion")


def main():
    rng = np.random.default_rng(20261021)
    jobs, labels = [], []
    for case_id, speed in SWEEP_BASELINES:
        design, task = baseline(case_id, speed, solved_only=True)
        for i in range(SAMPLES):
            d, _ = perturb(design, rng)
            jobs.append((d, task))
            labels.append((case_id, i))
    results = evaluate_many(jobs)
    out = {}
    for (case_id, i), res in zip(labels, results):
        out.setdefault(case_id, []).append({"sample": i, "status": res["status"], "error": (res["error"] or "")[:200],
                                            **{k: res["metrics"].get(k) for k in KEYS}})
    print(save("robustness", out))


if __name__ == "__main__":
    main()
