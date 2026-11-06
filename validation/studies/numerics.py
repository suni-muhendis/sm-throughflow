"""Study 1 and 2: determinism, and sensitivity to the numerical settings the task owns.

Determinism: each baseline is evaluated twice in one process and once in each of two other
processes; every metric must agree to the last bit. Numerics: stream-surface count, convergence
tolerance and the curvature model are varied one at a time from the task defaults.
"""
import copy

from common import BASELINES, baseline, evaluate, evaluate_many, save

KEYS = ("pressure_ratio_total", "efficiency_isentropic", "min_stall_margin", "max_relative_inlet_mach", "power_W")
SURFACES = (7, 11, 15, 21, 31)
TOLERANCES = (1e-5, 1e-6, 1e-7, 1e-8)
CURVATURES = ("full", "linear", "none")


def with_numerics(task, **numerics):
    t = copy.deepcopy(task)
    t.setdefault("numerics", {}).update(numerics)
    return t


def main():
    out = {"determinism": {}, "numerics": {}}
    jobs, labels = [], []
    for case_id, speed in BASELINES:
        design, task = baseline(case_id, speed)
        a, b = evaluate(design, task), evaluate(design, task)
        out["determinism"][case_id] = {"same_process_identical": a == b, "status": a["status"]}
        jobs += [(design, task), (design, task)]
        labels += [(case_id, "process", 0), (case_id, "process", 1)]
        for n in SURFACES:
            jobs.append((design, with_numerics(task, stream_surfaces=n)))
            labels.append((case_id, "stream_surfaces", n))
        for tol in TOLERANCES:
            jobs.append((design, with_numerics(task, tolerance=tol, max_iterations=3000)))
            labels.append((case_id, "tolerance", tol))
        for c in CURVATURES:
            jobs.append((design, with_numerics(task, curvature=c)))
            labels.append((case_id, "curvature", c))
        out["determinism"][case_id]["reference"] = a
    results = evaluate_many(jobs)
    for (case_id, kind, value), res in zip(labels, results):
        if kind == "process":
            ref = out["determinism"][case_id]["reference"]
            key = "cross_process_identical"
            out["determinism"][case_id][key] = out["determinism"][case_id].get(key, True) and res == ref
            continue
        out["numerics"].setdefault(case_id, {}).setdefault(kind, []).append(
            {"value": value, "status": res["status"], "error": res["error"], **{k: res["metrics"].get(k) for k in KEYS}})
    for d in out["determinism"].values():
        d["reference"] = {k: d["reference"]["metrics"].get(k) for k in KEYS}
    print(save("numerics", out))


if __name__ == "__main__":
    main()
