"""Compare all outcomes of the rejected research candidate to frozen v15."""
import argparse
from collections import Counter
import hashlib
import json
import zipfile
import numpy as np
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.probe_shock_coupled_v16 import BASELINE
from validation.screen_candidate_v16 import assess,ANCHORS
from validation.verify_family_source_v14 import verify
from validation.phase3 import statistics


def results(folder):
    return {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (folder/'results').glob('*.json')}


def main():
    p=argparse.ArgumentParser();p.add_argument('campaign');args=p.parse_args()
    campaign=ROOT/'validation/campaigns'/args.campaign
    source=verify(campaign);manifest=json.loads((campaign/'manifest.json').read_text())
    old,new=results(BASELINE),results(campaign)
    assert len(new)==108 and set(old)==set(new)
    assert json.loads((BASELINE/'jobs.json').read_text())==json.loads((campaign/'jobs.json').read_text())
    research=['validation/'+name+'.py' for name in ('compare_candidate_v16','probe_shock_coupled_v16','probe_shock_v16','shock_reference_v16')]
    with zipfile.ZipFile(campaign/'source.zip') as archive:
        assert all(archive.read(n)==(ROOT/n).read_bytes() for n in research)
    data=dict(source=source,research_scripts_byte_identical=True,screen=assess(old,new),
        counts={v:dict(Counter(r['classification'] for r in records.values())) for v,records in [('v15',old),('candidate',new)]})
    data['paired_errors']={}
    for rep in ('original','projected'):
        ids=[k for k,r in new.items() if r['representation']==rep and r['group']=='coupled' and r['converged'] and old[k]['converged']]
        data['paired_errors'][rep]=dict(count=len(ids),ids=ids,
            errors={v:{key:statistics(records[k]['errors'][key] for k in ids)
                for key in ('stage_pr_rise','stage_eta_points','rotor_tr_rise')}
                for v,records in [('v15',old),('candidate',new)]})
    data['preservation']={}
    fields=('converged','classification','metrics','diagnostics','stations','row_diagnostics')
    for rep in ('original','projected'):
        anchor=rep+'__nasa_stage35_100_3978';repeat=rep+'__anchor_repeat_0'
        data['preservation'][rep]=dict(repeat_equal=all(new[anchor].get(k)==new[repeat].get(k) for k in fields),
            checks={k:dict(v15=old[k]['classification'],candidate=new[k]['classification'],metrics_equal=old[k]['metrics']==new[k]['metrics'])
                for k in old if k.startswith(rep+'__') and any(tag in k for tag in ('nasa_stage53','nasa_stage35_90','anchor_duct_subdivisions','anchor_stream_surfaces'))})
    data['anchors']={rep:{s:dict(measured=old[f'{rep}__nasa_stage{s}_100_{rd}']['measurement']['stage_eta'],
        v15=old[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'].get('stage_eta'),
        candidate=new[f'{rep}__nasa_stage{s}_100_{rd}']['metrics'].get('stage_eta')) for s,rd in ANCHORS.items()}
        for rep in ('original','projected')}
    data['rows']={}
    for label,folder in [('v15',BASELINE),('candidate',campaign)]:
        rows=json.loads((folder/'rows.json').read_text());sens=json.loads((folder/'row_sensitivity.json').read_text())
        assert len(rows)==96 and len(sens)==6
        data['rows'][label]=dict(counts=dict(Counter(r['status'] for r in rows)),anchors=[])
        for r in rows:
            stage=next((s for s,rd in ANCHORS.items() if r['case']==f'nasa_stage{s}' and r['reading']==rd),None)
            if stage and 'points' in r:
                points=[q for q in r['points'] if q['core']]
                data['rows'][label]['anchors'].append(dict(stage=stage,row=r['row_type'],
                    measured_loss=float(np.mean([q['measured_loss'] for q in points])),
                    predicted_loss=float(np.mean([q['predicted_loss'] for q in points]))))
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in (BASELINE,campaign) for p in folder.rglob('*.json')}
    out=create_campaign(purpose='v16_candidate_rejection_analysis',selection=dict(
        baseline=BASELINE.name,candidate=campaign.name,release_evidence=False,input_sha256=hashes))
    write_json_new(out/'comparison.json',data)
    # Standalone scientific artifact, with units and no interpolated claims.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained');x=np.arange(4)
    for offset,key,label in [(-.25,'measured','Measured'),(0.,'v15','v15'),(.25,'candidate','Rejected shock candidate')]:
        ax.bar(x+offset,[100.*data['anchors']['original'][s][key] for s in ANCHORS],width=.24,label=label)
    ax.set_xticks(x,[f'Stage {s}' for s in ANCHORS]);ax.set_ylabel('Stage efficiency (%)');ax.set_ylim(0,100)
    ax.set_title('Same measured peak-flow anchors; original annulus');ax.legend(loc='lower center');ax.grid(axis='y',alpha=.2)
    fig.savefig(out/'family_efficiency.png',dpi=170);plt.close(fig)
    print(out);print(json.dumps(dict(counts=data['counts'],screen=data['screen'],preservation=data['preservation']),indent=2))


if __name__=='__main__':main()
