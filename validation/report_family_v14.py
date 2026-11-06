"""Matched v13/v14 evidence; failed outcomes and unfavorable family responses remain visible."""
import argparse
from collections import Counter
import hashlib
import json

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.compare_family_v14 import BASELINE
from validation.phase3 import PROTOCOL_PATH, plain, statistics
from validation.phase3_report import family_deltas, row_statistics
from sm_throughflow.provenance import runtime_identity
from validation.verify_family_source_v14 import verify

ANCHORS={35:'3978',36:'4272',37:'4182',38:'4120'}
PROBES=[]
OUTER_CAPTURE='20261105T083500953790Z_slc_aungier_experimental_v13'
ALTERNATE_ITERATION='20261105T085140237027Z_slc_aungier_experimental_v14'


def load_results(path):
    return {p.stem:json.loads(p.read_text()) for p in (path/'results').glob('*.json')}


def analyze(campaign):
    manifest=json.loads((campaign/'manifest.json').read_text())
    source_comparison=verify(campaign)
    assert not manifest['selection']['exploratory_subset']
    new,old=load_results(campaign),load_results(BASELINE)
    assert len(new)==108 and set(new)==set(old)
    evidence={}
    for path in (BASELINE,campaign,*(ROOT/'validation/campaigns'/p for p in [*PROBES,OUTER_CAPTURE,ALTERNATE_ITERATION])):
        m=json.loads((path/'manifest.json').read_text())
        assert hashlib.sha256((path/'source.zip').read_bytes()).hexdigest()==m['archive_sha256']
        evidence.update({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in path.rglob('*.json')})
    for name,value in manifest['selection']['baseline_evidence_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value
    output=create_campaign(purpose='v14_family_response_analysis',selection=dict(
        baseline=BASELINE.name,current=campaign.name,qualified=False,release_evidence=False))
    protocol=json.loads(PROTOCOL_PATH.read_text())
    summary,anchors,pairs,legacy={},{},{},{}
    for rep in ('original','projected'):
        group=[r for r in new.values() if r['representation']==rep]
        cohort=[r for r in group if r['group']=='coupled' and r['converged'] and old[r['id']]['converged']]
        anchor,repeat=(new[rep+'__'+k] for k in ('nasa_stage35_100_3978','anchor_repeat_0'))
        summary[rep]=dict(counts=dict(Counter(r['classification'] for r in group)),
            gained=[r['id'] for r in group if r['converged'] and not old[r['id']]['converged']],
            lost=[r['id'] for r in group if not r['converged'] and old[r['id']]['converged']],
            paired_success_count=len(cohort),paired_success_ids=[r['id'] for r in cohort],
            errors={key:{version:statistics((old[r['id']] if version=='v13' else r)['errors'][key] for r in cohort)
                         for version in ('v13','v14')} for key in ('stage_pr_rise','stage_eta_points','rotor_tr_rise')},
            repeat_converged=anchor['converged'] and repeat['converged'],
            repeat_bitwise_equal=all(anchor.get(k)==repeat.get(k) for k in
                ('converged','classification','metrics','diagnostics','stations','row_diagnostics')))
        anchors[rep]={}
        for stage,reading in ANCHORS.items():
            key=f'{rep}__nasa_stage{stage}_100_{reading}'
            r=new[key]
            anchors[rep][stage]=dict(id=key,measurement=r['measurement'],
                v13=old[key]['metrics'],v14=r['metrics'],classification=r['classification'])
        pairs[rep]=[]
        for a,b,change in ((35,36,'aspect_ratio_at_low_loading'),(37,38,'aspect_ratio_at_high_loading'),
                           (35,37,'loading_at_low_aspect_ratio'),(36,38,'loading_at_high_aspect_ratio')):
            values={version:100*(anchors[rep][b][version]['stage_eta']-anchors[rep][a][version]['stage_eta'])
                    if all('stage_eta' in anchors[rep][s][version] for s in (a,b)) else None
                    for version in ('measurement','v13','v14')}
            pairs[rep].append(dict(base=a,variant=b,comparison=change,eta_delta_points=values,
                pure_partial_derivative=False,release_evidence=False,
                limitation='Different measured peak-flow points and other blade/clearance differences. Loading comparisons are not a universal monotonicity law.'))
        legacy[rep]=family_deltas([dict(r,id=r['selection_id']) for r in group],protocol)
    rows=json.loads((campaign/'rows.json').read_text())
    prior_rows=json.loads((BASELINE/'rows.json').read_text())
    row_anchor=[]
    for rs,version in ((prior_rows,'v13'),(rows,'v14')):
        for r in rs:
            stage=next((s for s in ANCHORS if r['case']==f'nasa_stage{s}' and r['reading']==ANCHORS[s]),None)
            if stage is None or 'points' not in r:continue
            pts=[p for p in r['points'] if p['core']]
            row_anchor.append(dict(version=version,stage=stage,row=r['row_type'],
                equal_sample_core_means={k:float(np.mean([p[k] for p in pts])) for k in
                    ('measured_loss','predicted_loss','loss_error','measured_deviation','predicted_deviation','deviation_error')},
                independent_rotor_exit_measurement=False))
    components=[]
    for version,rs in (('v13',old),('v14',new)):
        for stage,reading in ANCHORS.items():
            r=rs[f'original__nasa_stage{stage}_100_{reading}']
            for name,d in r.get('row_diagnostics',{}).items():
                components.append(dict(version=version,stage=stage,row=name,equal_surface_means={
                    key:float(np.mean(d[key])) for key in ('design_loss','minimum_loss','shock_loss','profile_loss',
                    'clearance_loss','loss','deviation','relative_inlet_mach')},
                    weighting='Diagnostic unweighted span-surface means; not an additive efficiency budget'))
    probes=[]
    for name in PROBES:
        for r in load_results(ROOT/'validation/campaigns'/name).values():
            probes.append(dict(campaign=name,id=r['id'],mode=r['research_override'],classification=r['classification'],
                metrics=r['metrics'],release_evidence=False,
                uses_report_assumed_shock_location=r['research_override']=='published_phi',
                production_candidate=False))
    trace=json.loads((ROOT/'validation/campaigns'/OUTER_CAPTURE/'trace.json').read_text())[-20:]
    mach=[v['rows']['R1']['relative_inlet_mach'][9] for v in trace]
    shock=[v['rows']['R1']['shock_loss'][9] for v in trace]
    alternate_path=ROOT/'validation/campaigns'/ALTERNATE_ITERATION
    alternate=json.loads((alternate_path/'result.json').read_text())
    assert json.loads((alternate_path/'manifest.json').read_text())['runtime']['source_sha256']==runtime_identity()['source_sha256']
    current=new['original__nasa_stage53_100_2993']
    agreement={k:abs(current['metrics'][k]-alternate['metrics'][k]) for k in current['metrics']}
    assert current['converged'] and alternate['converged'] and max(agreement.values())<1e-10
    numerical=dict(captured_v13_surface=9,mach_range=[min(mach),max(mach)],pointwise_shock_range=[min(shock),max(shock)],
        current_stage53=current['metrics'],alternate_iteration_campaign=ALTERNATE_ITERATION,
        alternate_iteration_is_prototype=True,absolute_metric_differences=agreement,
        interpretation='Both iterations solve the same v14 equations; no extra physical validation follows.')
    clips=[dict(id=r['id'],row=name,surfaces=sum(d.get('shock_compression_clipped',[]))) for r in new.values()
           for name,d in r.get('row_diagnostics',{}).items() if any(d.get('shock_compression_clipped',[]))]
    assert len(rows)==len(prior_rows)==96
    direction_pass=all(p['eta_delta_points']['v14'] is not None and
        np.sign(p['eta_delta_points']['v14'])==np.sign(p['eta_delta_points']['measurement'])
        for ps in pairs.values() for p in ps)
    summary.update(qualified=False,training_design_ranking_qualified=False,
                   all_four_family_directions_agree=direction_pass,rows=len(rows),shock_compression_clips=clips)
    for name,value in [('source_comparison',source_comparison),('input_evidence_sha256',evidence),('summary',summary),('anchors',anchors),('paired_family',pairs),
                       ('legacy_family_deltas',legacy),('row_anchors',row_anchor),('loss_components',components),
                       ('counterfactuals',probes),('numerical_attribution',numerical),('row_statistics',row_statistics(rows,protocol))]:
        write_json_new(output/(name+'.json'),plain(value))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.5))
    for key,label,style in [('measurement','Experiment','ko-'),('v13','v13','s--'),('v14','v14','^-')]:
        ax.plot(list(ANCHORS),[100*anchors['original'][s][key]['stage_eta'] for s in ANCHORS],style,label=label)
    ax.set(xticks=list(ANCHORS),xlabel='Stage (each at its measured peak-flow anchor)',ylabel='Stage adiabatic efficiency (%)',
           title='Stage 35–38: matched geometry and shock integration comparison')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(output/'family_efficiency.png',dpi=160);plt.close(fig)
    print(output,flush=True)
    print(json.dumps(dict(counts={r:summary[r]['counts'] for r in ('original','projected')},pairs=pairs),indent=2))
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign')
    args=parser.parse_args()
    analyze(ROOT/'validation/campaigns'/args.campaign)
