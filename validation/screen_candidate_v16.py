"""Necessary development checks, not experimental qualification or a score.

Do not accept reduced absolute eta error as proof of correct design response.
Keep failed predictions in the report; never select a new predicted optimum.
"""
ANCHORS={35:'3978',36:'4272',37:'4182',38:'4120'}
PAIRS=((35,36),(37,38),(35,37),(36,38))


def assess(old,new):
    lost=sorted(k for k,r in old.items() if r['converged'] and
                (k not in new or not new[k]['converged']))
    pairs=[]
    for representation in ('original','projected'):
        for a,b in PAIRS:
            ids=[f'{representation}__nasa_stage{s}_100_{ANCHORS[s]}' for s in (a,b)]
            measured=100.*(old[ids[1]]['measurement']['stage_eta']-old[ids[0]]['measurement']['stage_eta'])
            values={}
            for label,results in (('v15',old),('candidate',new)):
                values[label]=(100.*(results[ids[1]]['metrics']['stage_eta']-results[ids[0]]['metrics']['stage_eta'])
                    if all(i in results and results[i]['converged'] and 'stage_eta' in results[i]['metrics'] for i in ids) else None)
            pairs.append(dict(representation=representation,base=a,variant=b,measured_delta_points=measured,
                **values,correct_direction=values['candidate'] is not None and measured*values['candidate']>0.))
    return dict(pairs=pairs,lost_converged_ids=lost,job_ids_identical=set(old)==set(new),
        necessary_development_checks_passed=not lost and set(old)==set(new) and all(p['correct_direction'] for p in pairs),
        experimentally_qualified=False,training_label_qualified=False,
        limitation='Necessary development screen only; same four development machines, no held-out or uncertainty qualification.')
