"""A favorable mean efficiency error must not hide reversed family response."""
from copy import deepcopy
from validation.screen_candidate_v16 import assess,ANCHORS


def records():
    eta={35:.845,36:.821,37:.840,38:.831}
    return {f'{rep}__nasa_stage{s}_100_{rd}':dict(converged=True,
        measurement=dict(stage_eta=eta[s]),metrics=dict(stage_eta=eta[s]))
        for rep in ('original','projected') for s,rd in ANCHORS.items()}


def test_matching_family_response_is_necessary_but_not_qualification():
    data=records();r=assess(data,data)
    assert r['necessary_development_checks_passed']
    assert not r['experimentally_qualified'] and not r['training_label_qualified']


def test_reversed_efficiency_direction_is_retained_and_rejected():
    old=records();new=deepcopy(old)
    new['original__nasa_stage36_100_4272']['metrics']['stage_eta']=.846
    r=assess(old,new)
    assert not r['necessary_development_checks_passed']
    bad=next(p for p in r['pairs'] if p['representation']=='original' and (p['base'],p['variant'])==(35,36))
    assert bad['candidate']>0>bad['measured_delta_points'] and not bad['correct_direction']


def test_missing_and_failed_predictions_cannot_disappear_from_cohort():
    old=records();new=deepcopy(old);missing=next(iter(new));del new[missing]
    failed=next(iter(new));new[failed].update(converged=False,metrics={})
    r=assess(old,new)
    assert r['lost_converged_ids']==sorted([missing,failed])
    assert not r['necessary_development_checks_passed'] and not r['job_ids_identical']
    assert any(p['candidate'] is None for p in r['pairs'])
