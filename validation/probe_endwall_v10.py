"""Capture the first failing v9 wall gap without modifying its equations."""
from dataclasses import asdict
import json
from pathlib import Path
import sys

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job, plain


class Captured(BaseException):
    pass


def main():
    from sm_throughflow.contracts import SIMULATOR_VERSION
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v9':
        raise ValueError('Replay this diagnostic with the archived v9 source; v10 refactors the wall march')
    jobs = json.loads((ROOT/'validation/campaigns/20261104T200124147703Z_slc_aungier_experimental_v9/jobs.json').read_text())
    campaign = create_campaign(purpose='v9_failed_endwall_gap_capture_before_v10', selection={
        'ids': ['original__anchor_gap_0.5', 'original__nasa_stage38_90_4133']})
    print(campaign, flush=True)
    source = (ROOT/'src/sm_throughflow/solver/endwall.py').read_text().splitlines()
    predictor_line = next(i+1 for i, line in enumerate(source) if 'for iteration in range(1, self.max_passes' in line)
    for job in jobs:
        if job['id'] not in ('original__anchor_gap_0.5', 'original__nasa_stage38_90_4133'):
            continue
        current = {}
        def trace(frame, event, arg):
            if frame.f_code.co_name != '_march' or not frame.f_code.co_filename.endswith('endwall.py'):
                return None
            v = frame.f_locals
            if event == 'call':
                current.clear()
            if (event == 'line' and frame.f_lineno == predictor_line
                    and (current.get('wall'), current.get('station')) != (v['wall'], v['q']+1)):
                b = v['blade']
                current.clear()
                current.update(e1=asdict(v['e1']), e2=asdict(v['e2']), s1=asdict(v['s1']), predictor=asdict(v['s2']),
                    initial=[v['X1'], v['M1'], v['T1']], omega_w=v['omega_w'],
                    blade=None if b is None else dict(g=b[0], gap=b[1], omega=b[2].omega),
                    delta_nu=v['self']._delta_nu.get(v['key'], 0.),
                    dvm_dm=v['dvm_dm'], f_me=v['f_me'], f_theta=v['f_theta'], dm=v['dm'],
                    wall=v['wall'], station=v['q']+1)
            if event == 'exception' and current:
                write_json_new(campaign/(job['id']+'.json'), plain(dict(inputs=current,
                    error=str(arg[1]), diagnostics=getattr(arg[1], 'diagnostics', {}))))
                raise Captured()
            return trace
        sys.settrace(trace)
        try:
            result = evaluate_job(job)
            print(job['id'], result['classification'], 'no wall failure captured', flush=True)
        except Captured:
            print(job['id'], 'captured', flush=True)
        finally:
            sys.settrace(None)


if __name__ == '__main__':
    main()
