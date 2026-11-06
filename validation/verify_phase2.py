"""Frozen Phase 2 numerical/path evidence and historical hole scope triage.

python validation/verify_phase2.py
No historical results are overwritten. This is not an empirical accuracy gate.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "validation"), str(ROOT / "validation" / "studies")]

from campaign import create_campaign, write_json_new
from scripts.run_throughflow import build_case
from sm_throughflow.offdesign import EnvironmentEvaluator, trace_map
from sm_throughflow.outcomes import failure_evidence
from sm_throughflow.provenance import runtime_identity


def historical_holes():
    """Reconstruct the old jobs without inferring the cause of an old failure."""
    import run as validation_run
    import sweeps
    import lewis_stage as L
    old_path = ROOT / "validation/studies/results/sweeps.json"
    admission_path = ROOT / "validation/studies/results/admission.json"
    old = json.loads(old_path.read_text())
    admitted = json.loads(admission_path.read_text())["points"]
    records, cache = [], {}
    for case_id, parameters in old.items():
        case = validation_run.CASES[case_id]()
        speed = 80 if case_id == "nasa_2stage_fan_tp1314" else 100
        readings = case.measured_points(speed)
        allowed = {p["reading"] for p in admitted.get(case_id, []) if p["status"] == "success"}
        readings = [p for p in readings if p["reading"] in allowed] or readings
        best = max(readings, key=lambda p: p.get("stage_eta", 0.0))
        task = L.task([("design", best["mass_flow"], best["rpm"])], inlet_blockage=case.inlet_blockage(speed))
        jobs, labels = sweeps.jobs_for(case_id, case.design, task)
        for parameter, points in parameters.items():
            good = [i for i, p in enumerate(points) if p["status"] == "success"]
            if not good:
                continue
            for i, historical in enumerate(points):
                if historical["status"] == "success" or not min(good) < i < max(good):
                    continue
                indices = [max(j for j in good if j < i), i, min(j for j in good if j > i)]
                neighbours = []
                for j in indices:
                    value = points[j]["value"]
                    matches = [k for k, label in enumerate(labels) if label[1] == parameter and abs(label[2] - value) < 1e-12]
                    assert len(matches) == 1, (case_id, parameter, value)
                    k = matches[0]
                    cache_key = (case_id, parameter, value)
                    if cache_key not in cache:
                        design, effective_task = jobs[k]
                        try:
                            evaluator = EnvironmentEvaluator(design, effective_task)
                            outcome = evaluator(effective_task["operating_points"][0]["mass_flow_kg_s"])
                            current = outcome.record()
                        except Exception as exc:
                            current = dict(converged=False, diagnostics=failure_evidence(exc), classification="input_or_adapter_failure")
                        cache[cache_key] = dict(value=value, design=design, task=effective_task, current=current)
                    neighbours.append(dict(cache[cache_key], historical=points[j]))
                records.append(dict(case=case_id, parameter=parameter, value=historical["value"],
                                    baseline_reading=best["reading"], neighbours=neighbours,
                                    disposition="outside_current_domain" if all(p["current"]["classification"] == "unsupported_condition" for p in neighbours)
                                    else "requires_case_specific_followup"))
    return dict(reconstruction="historical study code and solved-reading selection; original complete input records were not saved",
                source_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (old_path, admission_path)},
                holes=records, count=len(records),
                interpretation="A current scope exclusion bounds the claim; it does not explain or fix a historical numerical failure.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-only", action="store_true")
    args = parser.parse_args()
    output = create_campaign(purpose="phase2_classification_and_path_verification",
                             selection=dict(synthetic_flows=[77.6, 80., 82.4], historical_holes="all 39 with adjacent historical successes",
                                            historical_only=args.historical_only, empirical_acceptance=False))
    print(output, flush=True)
    if not args.historical_only:
        design, task = build_case(1)
        evaluator = EnvironmentEvaluator(design, task)
        audit = trace_map(evaluator, [77.6, 80., 82.4])
        write_json_new(output / "synthetic_map.json", dict(design=design, task=task, audit=audit, runtime=runtime_identity()))
        print("synthetic paths", [(p["mass_flow"], p["classification"]) for p in audit["points"]], flush=True)
        impossible = evaluator(500.)
        write_json_new(output / "physical_capacity.json", dict(design=design, task=task, requested_flow=500., outcome=impossible.record()))
        limited_task = copy.deepcopy(task)
        limited_task["numerics"].update(max_iterations=10, duct_subdivisions=16, repositioning="novak")
        limited = EnvironmentEvaluator(design, limited_task)(80.)
        write_json_new(output / "iteration_budget.json", dict(design=design, task=limited_task, outcome=limited.record()))
        print("capacity / limited iterations", impossible.classification, limited.classification, flush=True)
    holes = historical_holes()
    write_json_new(output / "historical_holes.json", holes)
    print("historical holes", holes["count"], "outside scope", sum(h["disposition"] == "outside_current_domain" for h in holes["holes"]), flush=True)


if __name__ == "__main__":
    main()
