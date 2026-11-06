"""Same frozen v15 experiment under v16 analytic MCA geometry; retain failures."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job, PROTOCOL_PATH, statistics
from validation.phase3_rows import run_rows
from validation.screen_candidate_v16 import assess, ANCHORS
from validation.verify_family_source_v14 import verify
from sm_throughflow.contracts import SIMULATOR_VERSION

BASELINE = ROOT/'validation/campaigns/20261105T095546195498Z_slc_aungier_experimental_v15'


def records(folder):
    return {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in (folder/'results').glob('*.json')}


def analyze(campaign):
    old, new = records(BASELINE), records(campaign)
    assert len(new) == 108 and set(new) == set(old)
    data = dict(source=verify(campaign), screen=assess(old, new),
                counts={v: dict(Counter(r['classification'] for r in rs.values())) for v, rs in [('v15', old), ('v16', new)]},
                anchors={}, paired_errors={}, preservation={})
    for rep in ('original', 'projected'):
        data['anchors'][rep] = {str(s): dict(
            measured=old[f'{rep}__nasa_stage{s}_100_{rd}']['measurement']['stage_eta'],
            v15=old[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'].get('stage_eta'),
            v16=new[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'].get('stage_eta')) for s, rd in ANCHORS.items()}
        ids = [k for k, r in new.items() if r['representation'] == rep and r['group'] == 'coupled' and r['converged'] and old[k]['converged']]
        data['paired_errors'][rep] = dict(count=len(ids), ids=ids,
            errors={v: {key: statistics(rs[k]['errors'][key] for k in ids)
                        for key in ('stage_pr_rise', 'stage_eta_points', 'rotor_tr_rise')}
                    for v, rs in [('v15', old), ('v16', new)]})
        anchor, repeat = [new[rep+'__'+key] for key in ('nasa_stage35_100_3978', 'anchor_repeat_0')]
        data['preservation'][rep] = dict(
            repeat_equal=all(anchor.get(k) == repeat.get(k) for k in ('converged', 'classification', 'metrics', 'diagnostics', 'stations', 'row_diagnostics')),
            checks={k: dict(v15=old[k]['classification'], v16=new[k]['classification'], metrics_equal=old[k]['metrics'] == new[k]['metrics'])
                    for k in old if k.startswith(rep+'__') and any(tag in k for tag in
                    ('nasa_stage53', 'nasa_stage35_90', 'anchor_duct_subdivisions', 'anchor_stream_surfaces'))})
    data['rows'] = {}
    for label, folder in [('v15', BASELINE), ('v16', campaign)]:
        rows = json.loads((folder/'rows.json').read_text())
        assert len(rows) == 96 and len(json.loads((folder/'row_sensitivity.json').read_text())) == 6
        data['rows'][label] = dict(Counter(r['status'] for r in rows))
    write_json_new(campaign/'analysis.json', data)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=3)
    args = parser.parse_args()
    assert SIMULATOR_VERSION == 'slc_aungier_experimental_v16'
    previous = json.loads((BASELINE/'jobs.json').read_text())
    jobs = deepcopy(previous)
    for old, job in zip(previous, jobs):
        job['task']['simulator_version'] = SIMULATOR_VERSION
        assert job['design'] == old['design'] and job['task'] == dict(old['task'], simulator_version=SIMULATOR_VERSION)
    evidence = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in BASELINE.rglob('*.json')}
    campaign = create_campaign(purpose='v16_analytic_mca_geometry_comparison', selection=dict(
        baseline=BASELINE.name, jobs=len(jobs), release_evidence=False, qualification=False,
        baseline_json_sha256=evidence, experimental_inputs_unchanged_except_version=True))
    write_json_new(campaign/'jobs.json', jobs)
    print(campaign, flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(evaluate_job, job) for job in jobs]):
            result = future.result()
            write_json_new(campaign/'results'/(result['id']+'.json'), result)
            print(result['id'], result['classification'], round(result['elapsed_seconds'], 1), flush=True)
    rows, sensitivity = run_rows(json.loads(PROTOCOL_PATH.read_text()))
    write_json_new(campaign/'rows.json', rows)
    write_json_new(campaign/'row_sensitivity.json', sensitivity)
    summary = analyze(campaign)
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == value for name, value in evidence.items())
    print(json.dumps(dict(counts=summary['counts'], screen=summary['screen'], anchors=summary['anchors'])), flush=True)
    print('COMPLETE', campaign, flush=True)


if __name__ == '__main__':
    main()
