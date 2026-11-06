"""Repeat the frozen v16 experiment under an explicitly unqualified override."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import PROTOCOL_PATH, statistics
from validation.phase3_rows import run_rows
from validation.probe_compressible_diffusion import run, BASELINE
from validation.compressible_diffusion_candidate import override, VERSION
from validation.screen_candidate_v16 import assess, ANCHORS
from validation.verify_family_source_v14 import verify


def records(folder):
    return {p.stem: json.loads(p.read_text()) for p in (folder/'results').glob('*.json')}


def analyze(folder):
    old, new = records(BASELINE), records(folder)
    assert len(new) == 108 and set(new) == set(old)
    screen = assess(old, new)
    for pair in screen['pairs']:
        pair['v16'] = pair.pop('v15')
    report = dict(source=verify(folder), production_unchanged=True, research_override=VERSION,
                  promoted=False, qualification=False, screen=screen,
                  counts={label: dict(Counter(r['classification'] for r in rows.values()))
                          for label, rows in [('v16',old),('candidate',new)]}, anchors={}, paired_errors={}, preservation={})
    for rep in ('original', 'projected'):
        report['anchors'][rep] = {str(s): dict(
            measured=old[f'{rep}__nasa_stage{s}_100_{rd}']['measurement']['stage_eta'],
            v16=old[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'].get('stage_eta'),
            candidate=new[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'].get('stage_eta')) for s,rd in ANCHORS.items()}
        ids = [k for k,r in new.items() if r['representation']==rep and r['group']=='coupled' and r['converged'] and old[k]['converged']]
        report['paired_errors'][rep] = dict(count=len(ids), ids=ids,
            errors={label: {key: statistics(rows[k]['errors'][key] for k in ids)
                           for key in ('stage_pr_rise','stage_eta_points','rotor_tr_rise')}
                    for label,rows in [('v16',old),('candidate',new)]})
        anchor, repeat = [new[rep+'__'+k] for k in ('nasa_stage35_100_3978','anchor_repeat_0')]
        report['preservation'][rep] = dict(
            repeat_equal=all(anchor.get(k)==repeat.get(k) for k in ('converged','classification','metrics','diagnostics','stations','row_diagnostics')),
            checks={k: dict(v16=old[k]['classification'], candidate=new[k]['classification']) for k in old
                    if k.startswith(rep+'__') and any(tag in k for tag in ('nasa_stage53','nasa_stage35_90','anchor_duct_subdivisions','anchor_stream_surfaces'))})
    for name, count in [('rows.json',96),('row_sensitivity.json',6)]:
        assert len(json.loads((folder/name).read_text())) == count
    write_json_new(folder/'analysis.json', report)
    return report


def main():
    jobs = json.loads((BASELINE/'jobs.json').read_text())
    evidence = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in BASELINE.rglob('*') if p.is_file()}
    out = create_campaign(purpose='v16_compressible_circulation_rejection_experiment', selection=dict(
        baseline=BASELINE.name, prototype=True, research_override=VERSION, jobs=108,
        release_evidence=False, training_label_qualified=False, experimental_inputs_unchanged=True,
        baseline_sha256=evidence))
    write_json_new(out/'jobs.json', jobs)
    print(out, flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(run,j) for j in jobs]):
            result = future.result()
            write_json_new(out/'results'/(result['id']+'.json'), result)
            print(result['id'], result['classification'], round(result['elapsed_seconds'],1), flush=True)
    with override():
        rows, sensitivity = run_rows(json.loads(PROTOCOL_PATH.read_text()))
    for r in rows+sensitivity:
        r.update(research_override=VERSION, prototype=True, release_evidence=False, training_label_qualified=False)
    write_json_new(out/'rows.json', rows)
    write_json_new(out/'row_sensitivity.json', sensitivity)
    report = analyze(out)
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value for name,value in evidence.items())
    print(json.dumps(dict(counts=report['counts'], screen=report['screen'], anchors=report['anchors'])), flush=True)
    print('COMPLETE',out,flush=True)


if __name__=='__main__':
    main()
