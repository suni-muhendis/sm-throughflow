"""Capture the first complete but unconverged full-loss iteration, research only."""
import json
import numpy as np
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.phase3 import evaluate_job,plain
from validation.probe_family_v14 import accelerated,BASELINE
from sm_throughflow.solver import throughflow as T

class Captured(BaseException):pass

def main():
    out=create_campaign(purpose='v14_capture_failed_outer',selection=dict(release_evidence=False))
    T.solve_quasi_normal=accelerated('aitken')
    original=T.Throughflow._solve
    trace=[]
    iterate=T.Throughflow._coupled_iteration
    def step(self,*args,**kwargs):
        r=iterate(self,*args,**kwargs)
        if self._loss_scale==1.:
            trace.append(dict(move=r[6],field=r[7],blockage_change=r[8],
                rows={name:{k:p.diagnostics[k] for k in ('relative_inlet_mach','shock_loss','minimum_loss','shock_flow_turning')}
                      for name,p in r[2].items()}))
        return r
    def solve(self,*args,**kwargs):
        sol=original(self,*args,**kwargs)
        if self._loss_scale==1. and not sol.convergence.converged:
            write_json_new(out/'trace.json',plain(trace));write_json_new(out/'positions.json',plain(sol.geometry.y/sol.geometry.y[:,-1:]));print(out,flush=True);raise Captured
        return sol
    T.Throughflow._coupled_iteration=step;T.Throughflow._solve=solve
    j=next(j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id']=='original__nasa_stage53_100_2993')
    try:evaluate_job(j)
    except Captured:pass

if __name__=='__main__':main()
