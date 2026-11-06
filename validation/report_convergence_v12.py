"""Complete v11/v12 comparison and independent wall-resolution diagnostics."""
import argparse
from collections import Counter
import hashlib
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.compare_convergence_v12 import BASELINE
from validation.phase3 import PROTOCOL_PATH, plain, statistics
from validation.phase3_report import coupled_profile, family_deltas, uncertainty_summary
from sm_throughflow.provenance import runtime_identity


def analyze(campaign, refinement):
    manifest = json.loads((campaign/'manifest.json').read_text())
    identity = runtime_identity()
    if manifest['runtime']['source_sha256'] != identity['source_sha256']:
        raise ValueError('Use the archived production source')
    if manifest['selection']['exploratory_subset']:
        raise ValueError('Complete comparison required')
    jobs = {j['id']: j for j in json.loads((campaign/'jobs.json').read_text())}
    new = {p.stem: json.loads(p.read_text()) for p in (campaign/'results').glob('*.json')}
    old = {p.stem: json.loads(p.read_text()) for p in (BASELINE/'results').glob('*.json')}
    if len(new) != 108 or set(new) != set(jobs) or set(new) != set(old):
        raise ValueError('All 108 matched outcomes required')
    rows = json.loads((campaign/'row_comparison.json').read_text())
    evidence = dict(manifest['selection']['baseline_evidence_sha256'])
    for path in (campaign, refinement):
        m = json.loads((path/'manifest.json').read_text())
        if m['runtime']['source_sha256'] != identity['source_sha256']:
            raise ValueError('Mixed production sources')
        if hashlib.sha256((path/'source.zip').read_bytes()).hexdigest() != m['archive_sha256']:
            raise ValueError('Archive checksum mismatch')
        evidence.update({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in path.rglob('*.json')})
    for name, value in manifest['selection']['baseline_evidence_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value:
            raise ValueError('Baseline evidence changed')
    output = create_campaign(purpose='v12_complete_comparison_analysis', selection=dict(
        coupled=campaign.name, refinement=refinement.name, release_evidence=False))
    write_json_new(output/'input_evidence_sha256.json', evidence)
    protocol = json.loads(PROTOCOL_PATH.read_text())
    summary, profiles, families, sensitivities = {}, {}, {}, {}
    for rep in ('projected', 'original'):
        group = [r for r in new.values() if r['representation'] == rep]
        coupled = [r for r in group if r['group'] == 'coupled']
        joint = [r for r in coupled if r['converged'] and old[r['id']]['converged']]
        summary[rep] = dict(
            counts={g: dict(Counter(r['classification'] for r in group if g == 'all' or r['group'] == g))
                    for g in ('all', 'coupled', 'clearance_family', 'sensitivity')},
            gained=[r['id'] for r in group if r['converged'] and not old[r['id']]['converged']],
            lost=[r['id'] for r in group if not r['converged'] and old[r['id']]['converged']],
            machines={name: dict(requested=len(items), converged=sum(r['converged'] for r in items))
                      for name in sorted(set(r['case'] for r in coupled))
                      for items in [[r for r in coupled if r['case'] == name]]},
            matched_success_cohort=dict(count=len(joint), ids=[r['id'] for r in joint], errors={key: {
                'baseline_v11': statistics(old[r['id']]['errors'][key] for r in joint),
                'current_v12': statistics(r['errors'][key] for r in joint)}
                for key in ('stage_pr_rise', 'stage_eta_points', 'rotor_tr_rise')}))
        profiles[rep] = [coupled_profile(r, jobs[r['id']]) for r in coupled if r['converged']]
        normalized = [dict(r, id=r['selection_id']) for r in group]
        families[rep] = family_deltas(normalized, protocol)
        sensitivities[rep] = uncertainty_summary(normalized)
        anchor, repeat = (new[rep+'__'+key] for key in ('nasa_stage35_100_3978', 'anchor_repeat_0'))
        summary[rep]['repeat_converged'] = anchor['converged'] and repeat['converged']
        summary[rep]['repeat_metrics_bitwise_equal'] = anchor['metrics'] == repeat['metrics'] if summary[rep]['repeat_converged'] else None
        summary[rep]['repeat_outcome_equal'] = all(anchor.get(k) == repeat.get(k) for k in
            ('converged', 'classification', 'metrics', 'diagnostics', 'stations', 'row_diagnostics'))
    refined = [json.loads(p.read_text()) for p in (refinement/'results').glob('*.json')]
    if len(refined) != 4:
        raise ValueError('All four refinement outcomes required')
    changes = []
    for r in refined:
        reference = new[r['reference_id']]
        changes.append(dict(id=r['id'], classification=r['classification'], substeps=r['value'],
            reference_id=r['reference_id'], reference_classification=reference['classification'],
            delta={k: r['metrics'][k]-reference['metrics'][k] for k in r['metrics'] if k in reference['metrics']},
            diagnostics=r['diagnostics'], release_evidence=False))
    summary.update(qualified=False, row_comparison=rows)
    for name, value in (('summary', summary), ('profiles', profiles), ('family_deltas', families),
                        ('sensitivity', sensitivities), ('wall_refinement', changes)):
        write_json_new(output/(name+'.json'), plain(value))
    print(output, flush=True)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    from pathlib import Path
    parser.add_argument('campaign', type=Path)
    parser.add_argument('refinement', type=Path)
    args = parser.parse_args()
    analyze(args.campaign.resolve(), args.refinement.resolve())
