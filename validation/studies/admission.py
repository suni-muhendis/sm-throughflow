"""Study 0: does the environment admit and solve the validation designs themselves?

Every validation case's design is evaluated through the environment at each measured design-speed
reading. The validation harness (validation/run.py) calls the solver directly and skips the design
rules, so this is the only place where the rules meet real machines.
"""
from common import L, R, evaluate_many, save
from sm_throughflow.contracts import ThroughflowDesignV2
from sm_throughflow.drc import run_drc


def main():
    jobs, labels, drc = [], [], {}
    for case_id in R.CASES:
        case = R.CASES[case_id]()
        ok, message = run_drc(ThroughflowDesignV2.model_validate(case.design))
        drc[case_id] = message if not ok else None
        speed = 100 if 100 in case.speeds else max(case.speeds, key=lambda s: -abs(s - 100))
        for p in case.measured_points(speed):
            task = L.task([("design", p["mass_flow"], p["rpm"])], inlet_blockage=case.inlet_blockage(speed))
            jobs.append((case.design, task))
            labels.append((case_id, speed, p["reading"], p["mass_flow"]))
    results = evaluate_many(jobs)
    out = {"drc": drc, "points": {}}
    for (case_id, speed, reading, m), res in zip(labels, results):
        out["points"].setdefault(case_id, []).append({"speed": speed, "reading": reading, "mass_flow": m, "status": res["status"],
                                                       "error": (res["error"] or "")[:200]})
    print(save("admission", out))


if __name__ == "__main__":
    main()
