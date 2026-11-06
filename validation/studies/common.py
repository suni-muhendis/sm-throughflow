"""Shared pieces of the internal-consistency studies: baseline designs, evaluation, result files.

Every study evaluates designs through the public environment (``sm_core.make_env``), exactly as a
benchmark or a training run would, so what it finds is what a learner would meet. The baselines are
the validation cases' own designs at the design-speed reading of highest measured efficiency.
"""
import json
import math
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATION = HERE.parent
sys.path[:0] = [str(VALIDATION), str(VALIDATION / "tools")]

import lewis_stage as L  # noqa: E402
import run as R  # noqa: E402

LEGACY_RESULTS = HERE / "results"
RESULTS = Path(os.environ["SM_THROUGHFLOW_STUDY_CAMPAIGN"]) / "results" if "SM_THROUGHFLOW_STUDY_CAMPAIGN" in os.environ else None

#: Baselines: a spread of the design space the validation covers (case id, speed %).
BASELINES = [
    ("nasa_stage35", 100),           # transonic MCA rotor, low aspect ratio
    ("nasa_stage37", 100),           # same rig, higher loading
    ("nasa_stage52", 100),           # fan stage, low hub-tip ratio
    ("nasa_stage55", 100),           # low-pressure-ratio fan
    ("nasa_stage6_1", 100),          # earlier transonic stage, part-span damper
    ("nasa_stage18_13", 100),        # highly loaded transonic stage, MCA, damper
    ("nasa_stage66_igv", 100),       # inlet stage with guide vanes
    ("nasa_2stage_fan_r67", 90),     # two-stage fan (design speed does not solve, see the report)
]


#: Baselines of the response studies: designs the environment admits, each at the reading of highest
#: measured efficiency among those it solves (from the admission study).
SWEEP_BASELINES = [
    ("nasa_stage35", 100), ("nasa_stage37", 100), ("nasa_stage53", 100), ("nasa_stage52", 100), ("nasa_stage14_10", 100),
    ("nasa_stage8_8", 100), ("nasa_stage6_1", 100), ("nasa_stage66_igv", 100), ("nasa_stage8e_c102", 100),
    ("nasa_2stage_fan_tp1314", 80),
]


def solved_readings(case_id):
    """Readings the environment solved in the admission study, or None if it has not run."""
    if RESULTS is None:
        return None
    path = RESULTS / "admission.json"
    if not path.exists():
        return None
    points = json.loads(path.read_text())["points"].get(case_id, [])
    return {p["reading"] for p in points if p["status"] == "success"}


def baseline(case_id, speed, solved_only=False):
    """(design, task) at the reading of highest measured stage efficiency at ``speed``; with
    ``solved_only``, among the readings the environment solves."""
    case = R.CASES[case_id]()
    points = case.measured_points(speed)
    if solved_only:
        ok = solved_readings(case_id)
        points = [p for p in points if ok is None or p["reading"] in ok] or points
    best = max(points, key=lambda p: p.get("stage_eta", 0.0))
    task = L.task([("design", best["mass_flow"], best["rpm"])], inlet_blockage=case.inlet_blockage(speed))
    return case.design, task


_ENV = None


def evaluate(design, task):
    """Metrics and status of one evaluation through the environment, warnings silenced."""
    global _ENV
    if _ENV is None:
        from sm_core import make_env
        _ENV = make_env("turbomachinery_throughflow")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = _ENV.evaluate("study", task, "study", design)
    if RESULTS is not None:
        from campaign import write_json_new
        from sm_throughflow.provenance import digest
        identity = digest({"design": design, "task": task})
        record = {"design": design, "task": task, "evaluation": res.model_dump(mode="json")}
        try:
            write_json_new(RESULTS.parent / "evaluations" / (identity + ".json"), record)
        except FileExistsError:
            pass  # repeated identical inputs within one frozen campaign
    return {"status": res.status, "metrics": dict(res.metrics or {}), "error": res.error_message}


def _call(job):
    return evaluate(*job)


def evaluate_many(jobs, workers=4):
    """Evaluate (design, task) pairs in parallel processes; results in input order."""
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_call, jobs, chunksize=1))


def save(name, data):
    if RESULTS is None:
        raise RuntimeError("run studies through run_all.py to create an immutable campaign")
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / (name + ".json")
    from campaign import write_json_new
    write_json_new(path, data)
    return path


def load(name):
    if RESULTS is None:
        raise RuntimeError("no current study campaign")
    return json.loads((RESULTS / (name + ".json")).read_text())
