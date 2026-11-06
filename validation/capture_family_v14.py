"""Capture the first v13 Stage 53 nonconvergent quasi-normal; diagnostic only."""
import inspect
import json
from pathlib import Path
import numpy as np
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job, plain
from sm_throughflow.solver import throughflow as T
from sm_throughflow.solver.errors import SolverError

BASELINE=ROOT/'validation/campaigns/20261104T232522087684Z_slc_aungier_experimental_v13'


class Captured(BaseException):pass


def main():
    job=next(j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id']=='original__nasa_stage53_100_2993')
    output=create_campaign(purpose='v14_stage53_quasi_normal_capture',selection=dict(baseline=BASELINE.name,job=job['id'],release_evidence=False))
    original=T.solve_quasi_normal
    signature=inspect.signature(original)
    def capture(*args,**kwargs):
        try:return original(*args,**kwargs)
        except SolverError as exc:
            if 'quasi-normal profile did not converge' not in str(exc):raise
            values=signature.bind(*args,**kwargs);values.apply_defaults();values=dict(values.arguments)
            gas=values.pop('gas');values['gas']=dict(cp=gas.cp,R=gas.R)
            write_json_new(output/'capture.json',plain(dict(inputs=values,failure=exc.diagnostics)))
            raise Captured
    T.solve_quasi_normal=capture
    try:evaluate_job(job)
    except Captured:print(output,flush=True)
    finally:T.solve_quasi_normal=original


if __name__=='__main__':main()
