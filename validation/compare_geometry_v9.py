"""Matched v8/v9 experiments: fixed inputs first, original annuli second.

Run: python -m validation.compare_geometry_v9 --workers 3
--ids is an exploratory subset, recorded as such; never a qualification run.
Old campaigns and the v8 preregistration are read-only evidence.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import admission, evaluate_job, gap_variant, plain, PROTOCOL_PATH
from validation.phase3_rows import run_rows
from validation import run as V
from sm_throughflow.contracts import SIMULATOR_VERSION

BASELINE = ROOT / 'validation/campaigns/20261104T184527810503Z_slc_aungier_experimental_v8'
BASELINE_ROWS = ROOT / 'validation/campaigns/20261104T184542071838Z_slc_aungier_experimental_v8'


def make_jobs(baseline):
    jobs = []
    for source in baseline:
        for representation in ('projected', 'original'):
            job = deepcopy(source)
            job.update(id=representation+'__'+source['id'], baseline_id=source['id'], representation=representation)
            if representation == 'original':
                design = deepcopy(V.CASES[source['case']]().design)
                if source.get('parameter') == 'gap':
                    design = gap_variant(design, source['value'])
                # Frozen blade perturbations/row placement, original wall controls.
                design['rows'] = deepcopy(source['design']['rows'])
                job['design'] = design
                job.pop('projection', None)
                job['geometry_interpretation'] = 'original_polyline_controls_with_interpolated_in_row_stream_surfaces'
            jobs.append(job)
    return jobs


def evaluate(job):
    job = deepcopy(job)
    job['effective_admission'] = admission(job['design'])
    return evaluate_job(job)


def summarize(results, baseline):
    rows = []
    for new in results:
        old = baseline[new['baseline_id']]
        rows.append(dict(id=new['id'], baseline_id=new['baseline_id'], representation=new['representation'],
                         group=new['group'], old_classification=old['classification'], new_classification=new['classification'],
                         admission=new['effective_admission'],
                         metric_delta={k: new['metrics'][k]-old['metrics'][k] for k in new['metrics'] if k in old['metrics']},
                         old_errors=old.get('errors'), new_errors=new.get('errors'),
                         old_elapsed_seconds=old['elapsed_seconds'], new_elapsed_seconds=new['elapsed_seconds']))
    counts = {rep: {group: dict(Counter(r['classification'] for r in results
                                      if r['representation'] == rep and (group == 'all' or r['group'] == group)))
                    for group in ('all', 'coupled', 'clearance_family', 'sensitivity')}
              for rep in ('projected', 'original')}
    return dict(counts=counts, matched_pairs=rows, qualified=False,
                interpretation='Numerical coverage and geometric sensitivity only; no correlation calibration or new empirical qualification.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=3, choices=range(1, 5))
    parser.add_argument('--ids', nargs='*')
    args = parser.parse_args()
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v9':
        raise RuntimeError('This comparison requires the v9 simulator.')
    baseline = json.loads((BASELINE / 'jobs.json').read_text())
    if args.ids:
        baseline = [j for j in baseline if j['id'] in args.ids]
        if {j['id'] for j in baseline} != set(args.ids):
            raise ValueError('Unknown baseline job ID')
    jobs = make_jobs(baseline)
    evidence = list(BASELINE.glob('results/*.json')) + [BASELINE/'jobs.json', BASELINE/'manifest.json',
               BASELINE_ROWS/'rows.json', BASELINE_ROWS/'row_sensitivity.json', PROTOCOL_PATH]
    frozen = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence}
    campaign = create_campaign(purpose='v9_geometry_and_numerical_comparison', selection=dict(
        exploratory_subset=bool(args.ids), jobs=len(jobs), baseline_jobs=len(baseline), baseline_sha256=frozen,
        selection_rule='exact archived v8 jobs; all failures retained; no selection on new results',
        numerical_budget='identical archived tasks, including 200 outer iterations per attempt and 1e-7 tolerance',
        geometric_model='blade-edge flow states, original interior wall controls, no internal blade forces',
        release_evidence=False))
    write_json_new(campaign/'jobs.json', jobs)
    print(campaign, flush=True)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = [pool.submit(evaluate, j) for j in jobs]
        for done in as_completed(pending):
            result = done.result()
            write_json_new(campaign/'results'/(result['id']+'.json'), result)
            results.append(result)
            print(result['id'], result['classification'], round(result['elapsed_seconds'], 1), flush=True)
    old = {j['id']: json.loads((BASELINE/'results'/(j['id']+'.json')).read_text()) for j in baseline}
    write_json_new(campaign/'comparison.json', plain(summarize(sorted(results, key=lambda r: r['id']), old)))
    if not args.ids:
        rows, sensitivity = run_rows(json.loads(PROTOCOL_PATH.read_text()))
        write_json_new(campaign/'rows.json', rows)
        write_json_new(campaign/'row_sensitivity.json', sensitivity)
        before = json.loads((BASELINE_ROWS/'rows.json').read_text())
        before_sensitivity = json.loads((BASELINE_ROWS/'row_sensitivity.json').read_text())
        # Admission metadata changes; physical closure arrays must not.
        def physical(records):
            return [{k: v for k, v in r.items() if k != 'original_admission'} for r in records]
        write_json_new(campaign/'row_comparison.json', dict(count=len(rows),
            closure_values_identical=physical(rows) == physical(before),
            sensitivity_values_identical=physical(sensitivity) == physical(before_sensitivity)))
    if any(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() != value for p, value in frozen.items()):
        raise RuntimeError('Historical evidence changed during the comparison')
    print('COMPLETE', campaign, flush=True)


if __name__ == '__main__':
    main()
