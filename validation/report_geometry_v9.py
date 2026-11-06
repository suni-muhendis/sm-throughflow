"""Analyze the complete matched campaign, keeping versions and cohorts separate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.compare_geometry_v9 import BASELINE
from validation.phase3 import admission, plain, projected_geometry, PROTOCOL_PATH, statistics
from validation.phase3_report import coupled_profile, family_deltas, uncertainty_summary
from validation import run as V
from sm_throughflow.provenance import runtime_identity


def analyze(campaign):
    manifest = json.loads((campaign/'manifest.json').read_text())
    if runtime_identity()['source_sha256'] != manifest['runtime']['source_sha256']:
        raise ValueError('Use the archived production source for this campaign')
    if hashlib.sha256((campaign/'source.zip').read_bytes()).hexdigest() != manifest['archive_sha256']:
        raise ValueError('Campaign source archive checksum mismatch')
    for name, expected in manifest['selection']['baseline_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Baseline evidence changed: '+name)
    if manifest['selection']['exploratory_subset']:
        raise ValueError('A complete matched campaign is required')
    jobs = {j['id']: j for j in json.loads((campaign/'jobs.json').read_text())}
    results = {p.stem: json.loads(p.read_text()) for p in (campaign/'results').glob('*.json')}
    baseline = {p.stem: json.loads(p.read_text()) for p in (BASELINE/'results').glob('*.json')}
    if len(jobs) != 108 or set(jobs) != set(results):
        raise ValueError('All 108 outcomes must be present')
    if not (campaign/'row_comparison.json').exists():
        raise ValueError('Measured-state closure rerun is incomplete')
    output = create_campaign(purpose='v9_matched_comparison_analysis', selection={'input_campaign': campaign.name})
    evidence = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(campaign.rglob('*.json'))}
    write_json_new(output/'input_evidence_sha256.json', evidence)
    protocol = json.loads(PROTOCOL_PATH.read_text())
    inventory = []
    for old in json.loads((BASELINE/'inventory.json').read_text()):
        design = V.CASES[old['case']]().design
        inventory.append(dict(case=old['case'], v8_original=old['original_admission'],
                              v9_original=admission(design),
                              v9_projected=admission(projected_geometry(design)[0])))
    write_json_new(output/'geometry_inventory.json', inventory)
    summary, profiles, family, uncertainty = {}, {}, {}, {}
    for representation in ('projected', 'original'):
        current = [r for r in results.values() if r['representation'] == representation]
        coupled = [r for r in current if r['group'] == 'coupled']
        admitted = [r for r in coupled if r['effective_admission']['passed']]
        joint = [r for r in coupled if r['converged'] and baseline[r['baseline_id']]['converged']]
        summary[representation] = dict(
            all_classifications=dict(Counter(r['classification'] for r in current)),
            experimental_classifications=dict(Counter(r['classification'] for r in coupled)),
            admitted_experimental_requested=len(admitted),
            admitted_experimental_converged=sum(r['converged'] for r in admitted),
            gained=[r['baseline_id'] for r in current if r['converged'] and not baseline[r['baseline_id']]['converged']],
            lost=[r['baseline_id'] for r in current if not r['converged'] and baseline[r['baseline_id']]['converged']],
            matched_success_cohort=dict(count=len(joint), ids=[r['baseline_id'] for r in joint],
                error_comparison={key: {'v8': statistics(baseline[r['baseline_id']]['errors'][key] for r in joint),
                                        'v9': statistics(r['errors'][key] for r in joint)}
                                  for key in ('stage_pr_rise', 'stage_eta_points', 'rotor_tr_rise')}),
            all_requested_error_statistics={key: statistics(r.get('errors', {}).get(key) for r in coupled)
                                            for key in ('stage_pr_rise', 'stage_eta_points', 'rotor_tr_rise')},
            machines={name: dict(requested=len(g), converged=sum(r['converged'] for r in g),
                                  admission=g[0]['effective_admission'])
                      for name in sorted(set(r['case'] for r in coupled))
                      for g in [[r for r in coupled if r['case'] == name]]})
        profiles[representation] = [coupled_profile(r, jobs[r['id']]) for r in coupled if r['converged']]
        # Helpers link anchors by their original IDs; undo only the namespace.
        normalized = [dict(r, id=r['baseline_id']) for r in current]
        family[representation] = family_deltas(normalized, protocol)
        uncertainty[representation] = uncertainty_summary(normalized)
        anchor = next(r for r in current if r['baseline_id'] == 'nasa_stage35_100_3978')
        repeat = next(r for r in current if r['baseline_id'] == 'anchor_repeat_0')
        summary[representation]['anchor_repeat_bitwise_equal'] = anchor['converged'] and repeat['converged'] and anchor['metrics'] == repeat['metrics']
    summary['qualified'] = False
    summary['qualification_reason'] = 'Numerical repair only. Closure errors, profile/design-response gates, uncertainty and independent holdout remain unresolved.'
    for name, data in (('summary', summary), ('profiles', profiles), ('family_deltas', family), ('uncertainty', uncertainty)):
        write_json_new(output/(name+'.json'), plain(data))
    render(output, results, baseline)
    print(output, flush=True)
    print(json.dumps(summary, indent=2))


def render(output, results, baseline):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    groups = [('v8 projected', [r for r in baseline.values() if r['group'] == 'coupled'])]
    groups += [(f'v9 {rep}', [r for r in results.values() if r['group'] == 'coupled' and r['representation'] == rep])
               for rep in ('projected', 'original')]
    axes[0].bar([name for name, _ in groups], [sum(r['converged'] for r in g) for _, g in groups], color=['#777777', '#3979ad', '#2f9074'])
    axes[0].axhline(33, color='k', ls='--', lw=1, label='33 requested experimental points')
    axes[0].set(ylabel='Converged / 33 requested', ylim=(0, 36))
    axes[0].legend(fontsize=8)
    common = set.intersection(*[{r.get('baseline_id', r['id']) for r in g if r['converged']} for _, g in groups])
    for i, (name, g) in enumerate(groups):
        points = sorted([r for r in g if r.get('baseline_id', r['id']) in common], key=lambda r: r.get('baseline_id', r['id']))
        axes[1].scatter(np.arange(len(points))+.15*(i-1), [r['errors']['stage_eta_points'] for r in points], label=name, s=22)
    axes[1].axhline(0, color='k', lw=.6)
    axes[1].set(xlabel=f'Same {len(common)} experimental points converged in all three groups', ylabel='Efficiency error (percentage points)')
    axes[1].legend(fontsize=8)
    fig.suptitle('Geometry and convergence repair: no empirical qualification')
    fig.savefig(output/'comparison.png', dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    analyze(parser.parse_args().campaign.resolve())
