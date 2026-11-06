"""Research-only inversion of TN D-7345 BLADE (printed pp. 144, 147).

No machine-dependent constants or experimental outputs enter the closure.
The source computes B2EQ from exit angular momentum at the inlet radius and
inlet meridional speed, then DKAPPA=(B1-B2EQ-CINC)/(1-DVC) and
SKOC=B2-DVC*DKAPPA. We invert these relations for a known blade geometry.
Retaining Aungier's off-design incidence slope is a hybrid assumption; this
probe is not production/release evidence even if its residuals converge.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import inspect
import json
import textwrap

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job, PROTOCOL_PATH, plain
from validation.phase3_rows import run_rows
from sm_throughflow.correlations import nasa_lewis as L
from sm_throughflow.solver import aungier_row as R

BASELINE = ROOT/'validation/campaigns/20261105T085249763272Z_slc_aungier_experimental_v14'


def equivalent_deviation(g, wm1, wm2, r1, r2, signed_omega):
    q = L.carter_deviation_coefficient(g['stagger'], g['a_c']) / np.sqrt(g['sigma'])
    if np.any((q < 0.) | (q >= 1.)):
        raise ValueError('equivalent Carter inversion requires 0 <= m/sqrt(sigma) < 1')
    a = (r2/r1)*(wm2/wm1)
    b = signed_omega*(r2*r2-r1*r1)/(r1*wm1)
    lo, hi = np.full_like(q, -89.999999), np.full_like(q, 89.999999)
    # The derivative is 1-q+q*a*sec(beta)^2/(1+(a*tan(beta)+b)^2)>0.
    for _ in range(48):
        beta = (lo+hi)*.5
        beta_eq = np.degrees(np.arctan(a*np.tan(np.radians(beta))+b))
        residual = (1-q)*(beta-g['k2'])+q*(beta_eq-g['k1'])
        lo, hi = np.where(residual < 0, beta, lo), np.where(residual >= 0, beta, hi)
    return (lo+hi)*.5-g['k2']


def install(mode='coupled'):
    original = textwrap.dedent(inspect.getsource(R.AungierCompressorRow.__call__))
    replacement = '''# Research-only TN D-7345 equivalent-camber inversion.
    equivalent_delta = None
    if self.camberline == "multiple_circular_arc" and not self.inlet_guide_vane:
        equivalent_delta = equivalent_deviation(g, wm1, wm2, r1, r2, sign*omega)
        if equivalent_mode == 'coupled':
            delta_star = equivalent_delta
    # Design loss at the design incidence'''
    original = original.replace('# Design loss at the design incidence', replacement)
    marker = '    beta2 = k2 + delta\n'
    assert original.count(marker) == 1
    original = original.replace(marker, '''    if equivalent_delta is not None:
        delta = equivalent_delta + slope*(incidence-i_star)
    beta2 = k2 + delta
''')
    scope = dict(vars(R), equivalent_deviation=equivalent_deviation, equivalent_mode=mode)
    exec(compile(original, __file__+':research_override', 'exec'), scope)
    R.AungierCompressorRow.__call__ = scope['__call__']


def run(job, mode):
    # Spawned process installs once; pool children may handle multiple jobs.
    if not getattr(R.AungierCompressorRow, '_equivalent_probe', False):
        install(mode)
        R.AungierCompressorRow._equivalent_probe = True
    result = evaluate_job(job)
    result.update(prototype=True, research_override='equivalent_carter_'+mode, release_evidence=False)
    return result


def main():
    from sm_throughflow.contracts import SIMULATOR_VERSION
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v14':
        raise ValueError('This research override requires the archived v14 production source')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=('coupled', 'deviation_only'), default='coupled')
    p.add_argument('--full', action='store_true')
    p.add_argument('--all-jobs', action='store_true')
    args = p.parse_args()
    campaign = create_campaign(purpose='v15_equivalent_camber_research', selection=dict(
        prototype=True, mode=args.mode, baseline=BASELINE.name, release_evidence=False,
        source='NASA TN D-7345 BLADE printed pp. 144, 147',
        assumption='Aungier off-design incidence slope retained; velocity term replaced'))
    print(campaign, flush=True)
    if args.full:
        ids = ['original__nasa_stage'+str(n)+'_100_'+rd for n, rd in
               [(35, '3978'), (36, '4272'), (37, '4182'), (38, '4120'), (53, '2993')]]
        jobs = [j for j in json.loads((BASELINE/'jobs.json').read_text(encoding='utf-8'))
                if args.all_jobs or j['id'] in ids]
        write_json_new(campaign/'jobs.json', jobs)
        with ProcessPoolExecutor(max_workers=3) as pool:
            for f in as_completed([pool.submit(run, j, args.mode) for j in jobs]):
                result = f.result()
                write_json_new(campaign/'results'/(result['id']+'.json'), result)
                print(result['id'], result['classification'], result['metrics'], flush=True)
    install(args.mode)
    rows, sensitivity = run_rows(json.loads(PROTOCOL_PATH.read_text(encoding='utf-8')))
    write_json_new(campaign/'rows.json', rows)
    write_json_new(campaign/'row_sensitivity.json', sensitivity)
    for row in rows:
        if row['case'] not in ['nasa_stage'+str(n) for n in (35, 36, 37, 38)]:
            continue
        if row.get('reading') not in ('3978', '4272', '4182', '4120'):
            continue
        pts = [v for v in row.get('points', []) if v['core']]
        print(row['case'], row['reading'], row['row_type'], plain({
            key: np.mean([v[key] for v in pts]) for key in
            ('measured_deviation', 'predicted_deviation', 'measured_loss', 'predicted_loss')
        }), flush=True)
    print('COMPLETE', campaign, flush=True)


if __name__ == '__main__':
    main()
