"""Frozen v14 jobs rerun under v15, retaining every outcome and version."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job, PROTOCOL_PATH
from validation.phase3_rows import run_rows
from validation.compare_geometry_v9 import summarize
from sm_throughflow.contracts import SIMULATOR_VERSION

BASELINE = ROOT/'validation/campaigns/20261105T085249763272Z_slc_aungier_experimental_v14'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=3)
    parser.add_argument('--ids', nargs='*')
    args = parser.parse_args()
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v15':
        raise ValueError('v15 required')
    jobs = deepcopy(json.loads((BASELINE/'jobs.json').read_text()))
    if args.ids:
        jobs = [j for j in jobs if j['id'] in args.ids]
        if {j['id'] for j in jobs} != set(args.ids):
            raise ValueError('Unknown job ID')
    old = {j['id']: json.loads((BASELINE/'results'/(j['id']+'.json')).read_text()) for j in jobs}
    for job in jobs:
        prior = deepcopy(job)
        job['selection_id'] = job.get('selection_id', job['baseline_id'])
        job['baseline_id'] = job['id']
        job['task']['simulator_version'] = SIMULATOR_VERSION
        job['task']['numerics']['endwall_subdivisions'] = 8
        job['effective_admission'] = old[job['id']]['effective_admission']
        expected_task = deepcopy(prior['task'])
        expected_task['simulator_version'] = SIMULATOR_VERSION
        assert job['design'] == prior['design'] and job['task'] == expected_task
    evidence = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in BASELINE.rglob('*.json')}
    campaign = create_campaign(purpose='v15_equivalent_camber_comparison', selection=dict(
        baseline_campaign=BASELINE.name, exploratory_subset=bool(args.ids), jobs=len(jobs),
        baseline_evidence_sha256=evidence, endwall_subdivisions=8, release_evidence=False))
    write_json_new(campaign/'jobs.json', jobs)
    print(campaign, flush=True)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = [pool.submit(evaluate_job, j) for j in jobs]
        for future in as_completed(pending):
            result = future.result()
            write_json_new(campaign/'results'/(result['id']+'.json'), result)
            results.append(result)
            print(result['id'], result['classification'], round(result['elapsed_seconds'], 1), flush=True)
    write_json_new(campaign/'comparison.json', summarize(sorted(results, key=lambda r: r['id']), old))
    if not args.ids:
        rows, sensitivity = run_rows(json.loads(PROTOCOL_PATH.read_text()))
        write_json_new(campaign/'rows.json', rows)
        write_json_new(campaign/'row_sensitivity.json', sensitivity)
        write_json_new(campaign/'row_comparison.json', dict(count=len(rows),
            closure_values_identical=rows == json.loads((BASELINE/'rows.json').read_text()),
            sensitivity_values_identical=sensitivity == json.loads((BASELINE/'row_sensitivity.json').read_text())))
    if any(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value for name, value in evidence.items()):
        raise RuntimeError('Baseline evidence changed')
    print('COMPLETE', campaign, flush=True)


if __name__ == '__main__':
    main()
