"""Paired v14/v15 results; retain failures and unfavorable efficiency responses."""
import argparse
from collections import Counter
import hashlib
import json

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.compare_family_v15 import BASELINE
from validation.phase3 import PROTOCOL_PATH, plain, statistics
from validation.phase3_report import row_statistics
from validation.verify_family_source_v14 import verify

ANCHORS = {35:'3978', 36:'4272', 37:'4182', 38:'4120'}
PROBES = ['20261105T094647238537Z_slc_aungier_experimental_v14',
          '20261105T094819176607Z_slc_aungier_experimental_v14']


def results(folder):
    return {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (folder/'results').glob('*.json')}


def analyze(campaign):
    source = verify(campaign)
    manifest = json.loads((campaign/'manifest.json').read_text(encoding='utf-8'))
    assert not manifest['selection']['exploratory_subset']
    old, new = results(BASELINE), results(campaign)
    assert len(new) == 108 and set(new) == set(old)
    jobs = json.loads((campaign/'jobs.json').read_text(encoding='utf-8'))
    old_jobs = {j['id']:j for j in json.loads((BASELINE/'jobs.json').read_text(encoding='utf-8'))}
    for j in jobs:
        prior = old_jobs[j['id']]
        assert j['design'] == prior['design']
        assert j['task'] == dict(prior['task'], simulator_version=j['task']['simulator_version'])
    summary, anchors, pairs = {}, {}, {}
    for rep in ('original', 'projected'):
        group = [r for r in new.values() if r['representation'] == rep]
        paired = [r for r in group if r['group'] == 'coupled' and r['converged'] and old[r['id']]['converged']]
        anchor, repeat = (new[rep+'__'+name] for name in ('nasa_stage35_100_3978', 'anchor_repeat_0'))
        summary[rep] = dict(counts=dict(Counter(r['classification'] for r in group)),
            gained=[r['id'] for r in group if r['converged'] and not old[r['id']]['converged']],
            lost=[r['id'] for r in group if not r['converged'] and old[r['id']]['converged']],
            paired_success_count=len(paired), paired_success_ids=[r['id'] for r in paired],
            errors={key:{v:statistics((old[r['id']] if v=='v14' else r)['errors'][key] for r in paired)
                         for v in ('v14','v15')} for key in ('stage_pr_rise','stage_eta_points','rotor_tr_rise')},
            repeat_bitwise_equal=all(anchor.get(k)==repeat.get(k) for k in
                ('converged','classification','metrics','diagnostics','stations','row_diagnostics')))
        anchors[rep] = {s:dict(id=f'{rep}__nasa_stage{s}_100_{rd}',
            measurement=new[f'{rep}__nasa_stage{s}_100_{rd}']['measurement'],
            **{v:rs[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'] for v,rs in [('v14',old),('v15',new)]})
            for s,rd in ANCHORS.items()}
        pairs[rep] = []
        for a,b,change in [(35,36,'aspect_ratio_at_low_loading'), (37,38,'aspect_ratio_at_high_loading'),
                           (35,37,'loading_at_low_aspect_ratio'), (36,38,'loading_at_high_aspect_ratio')]:
            deltas = {v:100*(anchors[rep][b][v]['stage_eta']-anchors[rep][a][v]['stage_eta'])
                      if all('stage_eta' in anchors[rep][s][v] for s in (a,b)) else None
                      for v in ('measurement','v14','v15')}
            pairs[rep].append(dict(base=a,variant=b,comparison=change,eta_delta_points=deltas,
                pure_partial_derivative=False,release_evidence=False,
                limitation='Different measured peak-flow anchors and other geometry/clearance differences.'))
    row_anchors, components, row_summaries, probe_summary = [], [], {}, []
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding='utf-8'))
    for version, folder in [('v14',BASELINE), ('v15',campaign), *[(p, ROOT/'validation/campaigns'/p) for p in PROBES]]:
        rows = json.loads((folder/'rows.json').read_text(encoding='utf-8'))
        assert len(rows) == 96
        row_summaries[version] = row_statistics(rows, protocol)
        for row in rows:
            stage = next((s for s,rd in ANCHORS.items() if row['case']==f'nasa_stage{s}' and row['reading']==rd), None)
            if stage is None or 'points' not in row: continue
            core = [p for p in row['points'] if p['core']]
            row_anchors.append(dict(version=version,stage=stage,row=row['row_type'],
                equal_sample_core_means={k:float(np.mean([p[k] for p in core])) for k in
                ('measured_loss','predicted_loss','loss_error','measured_deviation','predicted_deviation','deviation_error')},
                independent_rotor_exit_measurement=False))
        if version in PROBES:
            probe_summary.append(dict(campaign=version,prototype=True,release_evidence=False,
                outcomes={k:dict(classification=r['classification'],metrics=r['metrics']) for k,r in results(folder).items()}))
    for v, rs in [('v14',old),('v15',new)]:
        for stage,rd in ANCHORS.items():
            for row,d in rs[f'original__nasa_stage{stage}_100_{rd}'].get('row_diagnostics',{}).items():
                components.append(dict(version=v,stage=stage,row=row,equal_surface_means={
                    k:float(np.mean(d[k])) for k in ('design_loss','minimum_loss','shock_loss','profile_loss',
                        'clearance_loss','loss','deviation','design_deviation','relative_inlet_mach')},
                    weighting='Unweighted diagnostic surface means; not an additive efficiency budget'))
    clips = [dict(id=r['id'],row=n) for r in new.values() for n,d in r.get('row_diagnostics',{}).items()
             if any(d.get('shock_compression_clipped',[]))]
    stage53 = 'original__nasa_stage53_100_2993'
    summary.update(qualified=False,training_design_ranking_qualified=False,
        all_four_family_directions_agree=all(p['eta_delta_points']['v15'] is not None and
            np.sign(p['eta_delta_points']['v15'])==np.sign(p['eta_delta_points']['measurement'])
            for ps in pairs.values() for p in ps),
        stage53=dict(classification=new[stage53]['classification'],metrics=new[stage53]['metrics'],
            metrics_bitwise_equal_v14=new[stage53]['metrics']==old[stage53]['metrics']),
        shock_compression_clips=clips)
    evidence = {}
    for folder in [BASELINE,campaign,*[ROOT/'validation/campaigns'/p for p in PROBES]]:
        m = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        assert hashlib.sha256((folder/'source.zip').read_bytes()).hexdigest()==m['archive_sha256']
        evidence.update({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in folder.rglob('*.json')})
    for k,v in manifest['selection']['baseline_evidence_sha256'].items():
        assert hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v
    output = create_campaign(purpose='v15_equivalent_camber_analysis', selection=dict(
        baseline=BASELINE.name,current=campaign.name,qualified=False,release_evidence=False))
    for name,value in [('summary',summary),('anchors',anchors),('paired_family',pairs),('row_anchors',row_anchors),
                       ('row_statistics',row_summaries),('loss_components',components),('counterfactuals',probe_summary),
                       ('source_comparison',source),('input_evidence_sha256',evidence)]:
        write_json_new(output/(name+'.json'),plain(value))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.5))
    for key,label,style in [('measurement','Experiment','ko-'),('v14','v14','s--'),('v15','v15','^-')]:
        ax.plot(list(ANCHORS),[100*anchors['original'][s][key]['stage_eta'] for s in ANCHORS],style,label=label)
    ax.set(xticks=list(ANCHORS),xlabel='Stage (each at its measured peak-flow anchor)',
           ylabel='Stage adiabatic efficiency (%)',title='Equivalent camber: consistency correction, unresolved ordering')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(output/'family_efficiency.png',dpi=160);plt.close(fig)
    print(output,flush=True)
    print(json.dumps(dict(counts={r:summary[r]['counts'] for r in ('original','projected')},pairs=pairs),indent=2))
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('campaign');args=p.parse_args()
    analyze(ROOT/'validation/campaigns'/args.campaign)
