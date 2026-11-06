"""Temporary v13 numerical probes; immutable diagnostic outputs, no release evidence."""
import argparse
import inspect
import json
import numpy as np
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.phase3 import evaluate_job,plain
from sm_throughflow.solver import throughflow as T,quasi_normal as Q
from sm_throughflow.solver.gas import PerfectGas

BASELINE=ROOT/'validation/campaigns/20261104T232522087684Z_slc_aungier_experimental_v13'
CAPTURE=ROOT/'validation/campaigns/20261105T080935086331Z_slc_aungier_experimental_v13/capture.json'


def accelerated(mode):
    source=inspect.getsource(Q.solve_quasi_normal)
    if mode=='damped':source=source.replace('            Wm = new','            Wm = .5*Wm+.5*new')
    elif mode=='aitken':
        source=source.replace('        change = float("inf")','        change = float("inf")\n        previous=None\n        relax=1.')
        source=source.replace('            Wm = new','''            residual=new-Wm
            if previous is not None:
                difference=residual-previous
                den=float(difference@difference)
                if den>1e-28:
                    relax=float(np.clip(-relax*(previous@difference)/den,.05,2.))
            weight=relax
            candidate=Wm+weight*residual
            while np.any(candidate<=0.) or np.any(thermo(candidate)[2]<=0.):
                weight*=.5
                candidate=Wm+weight*residual
                if weight<1e-8:
                    candidate=new
                    weight=1.
                    break
            previous=residual
            relax=weight
            Wm=candidate''')
    else:raise ValueError(mode)
    scope=dict(Q.__dict__);exec(source,scope)
    return scope['solve_quasi_normal']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['aitken','damped']);parser.add_argument('--full',action='store_true')
    parser.add_argument('--rcond',type=float);parser.add_argument('--depth',type=int);args=parser.parse_args()
    candidate=accelerated(args.mode)
    values=json.loads(CAPTURE.read_text())['inputs'];gas=PerfectGas(**values.pop('gas'))
    values={k:np.array(v) if isinstance(v,list) else v for k,v in values.items()}
    try:
        st=candidate(gas,**values);print('CAPTURE RECOVERED',st.solver_diagnostics,flush=True)
    except Exception as exc:print('CAPTURE FAILED',str(exc),getattr(exc,'diagnostics',{}),flush=True)
    if not args.full:return
    job=next(j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id']=='original__nasa_stage53_100_2993')
    from sm_throughflow.contracts import SIMULATOR_VERSION
    job['task']['simulator_version']=SIMULATOR_VERSION
    if args.rcond is not None:
        from sm_throughflow.solver import reposition as R
        source=inspect.getsource(R.CoupledRepositioning).replace('rcond=1e-10',f'rcond={args.rcond!r}')
        if args.depth is not None:source=source.replace('self.depth = depth',f'self.depth = {args.depth}')
        scope=dict(R.__dict__);exec(source,scope);T.CoupledRepositioning=scope['CoupledRepositioning']
    output=create_campaign(purpose='v14_numerical_counterfactual',selection=dict(mode=args.mode,rcond=args.rcond,depth=args.depth,baseline=BASELINE.name,release_evidence=False))
    T.solve_quasi_normal=candidate
    result=evaluate_job(job);result.update(prototype=True,research_override=args.mode,release_evidence=False)
    write_json_new(output/'result.json',result)
    print(output,result['classification'],result['metrics'],flush=True)


if __name__=='__main__':main()
