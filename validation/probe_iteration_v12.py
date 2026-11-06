"""Explicit v11 research overrides; not released-simulator evidence."""
import argparse
import inspect
import json
import textwrap
from copy import deepcopy
from time import perf_counter
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import plain, report_overall
from sm_throughflow.contracts import ThroughflowTaskV2, ThroughflowDesignV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.reposition import CoupledRepositioning
import sm_throughflow.solver.endwall as ew

BASELINE = ROOT/'validation/campaigns/20261104T220638956907Z_slc_aungier_experimental_v11'


def elliptic(geo, stations, residual):
    nq, ns = residual.shape
    ni = ns-2
    radial = lil_matrix((nq*ni,nq*ni))
    axial = lil_matrix(radial.shape)
    for q in range(nq):
        for j in range(1,ns-1):
            k = q*ni+j-1
            left, right = np.diff(geo.y[q,j-1:j+2])
            a, b = 2/(left*(left+right)), 2/(right*(left+right))
            radial[k,k] = a+b
            if j>1: radial[k,k-1] = -a
            if j<ns-2: radial[k,k+1] = -b
            if 0<q<nq-1:
                left, right = np.diff(geo.m[q-1:q+2,j])
                c = 1-min(stations[q].Wm[j]/stations[q].a[j],.95)**2
                a, b = 2*c/(left*(left+right)), 2*c/(right*(left+right))
                axial[k,k] = a+b
                axial[k,k-ni],axial[k,k+ni] = -a,-b
    height = geo.y[:,-1:]
    correction = np.zeros_like(residual)
    correction[:,1:-1] = spsolve((radial+axial).tocsr(),radial.tocsr()@(residual*height)[:,1:-1].ravel()).reshape(nq,ni)
    return correction/height


def install(flow, wall_count, precondition, relaxation=1.):
    if wall_count:
        namespace = dict(vars(ew))
        source = textwrap.dedent(inspect.getsource(ew.EndwallBoundaryLayers._integrate_gap))
        source = source.replace('self.subdivisions if blade is not None else 1',str(wall_count)+' if blade is None else self.subdivisions')
        exec(source,namespace)
        flow.endwall._integrate_gap = namespace['_integrate_gap'].__get__(flow.endwall)
    if not precondition:return
    original = flow._coupled_iteration
    latest = {}
    def coupled(t,*args):
        result = original(t,*args)
        latest.update(correction=relaxation*elliptic(result[0],result[1],result[5]-t),residual=result[5]-t)
        return result
    flow._coupled_iteration = coupled
    def damping(*args):
        r = latest['residual']
        return np.divide(latest['correction'],r,out=np.ones_like(r),where=r!=0.)
    flow._damping = damping
    def step(self,t,target,damping,blockage,next_blockage,relaxation,minimum_blockage):
        x=np.r_[t.ravel(),blockage]
        f=np.r_[(damping*(target-t)).ravel(),next_blockage-blockage]
        raw=np.r_[(target-t).ravel(),(next_blockage-blockage)/relaxation]
        self.history.append((x.copy(),f.copy(),raw.copy()))
        self.history=self.history[-self.depth-1:]
        candidate=x+f
        if len(self.history)>=3:
            dx,df,dr=[np.column_stack([b[k]-a[k] for a,b in zip(self.history,self.history[1:])]) for k in range(3)]
            coefficients=np.linalg.lstsq(dr,raw,rcond=1e-10)[0]
            trial=candidate-(dx+df)@coefficients
            pos=trial[:t.size].reshape(t.shape)
            kb=trial[t.size:]
            if np.all(np.isfinite(trial)) and np.max(np.abs(pos-t))<.03 and np.all(np.diff(pos,axis=1)>0) and np.all((kb>=minimum_blockage)&(kb<=1.)):
                candidate=trial;self.accepted+=1
            else:self.rejected+=1;self.history=self.history[-1:]
        pos=candidate[:t.size].reshape(t.shape)
        pos[:,0],pos[:,-1]=0.,1.
        return pos,candidate[t.size:].copy()
    CoupledRepositioning.step=step


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--id',default='projected__nasa_stage35_90_3979')
    parser.add_argument('--wall',type=int,default=0)
    parser.add_argument('--precondition',action='store_true')
    parser.add_argument('--grids',type=int,nargs='+',default=[1])
    parser.add_argument('--budget',type=int,default=200)
    parser.add_argument('--relax',type=float,default=1.)
    args=parser.parse_args()
    output=create_campaign(purpose='v12_iteration_research_on_v11',selection=dict(vars(args),prototype=True,release_evidence=False))
    print(output,flush=True)
    source=next(j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id']==args.id)
    seed=None
    for count in args.grids:
        job=deepcopy(source)
        job['task']['numerics'].update(duct_subdivisions=count,max_iterations=args.budget)
        task=ThroughflowTaskV2.model_validate(job['task'])
        flow,_=SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(job['design']),task,task.operating_points[0])
        install(flow,args.wall,args.precondition,args.relax)
        trace=[]
        original=flow._coupled_iteration
        def traced(*a):
            result=original(*a)
            trace.append([flow._effort['outer_iterations'],*result[6:]])
            return result
        flow._coupled_iteration=traced
        positions=None if seed is None else np.column_stack([np.interp(flow.qn.z_hub,seed['z'][:,k],seed['t'][:,k]) for k in range(flow.n)])
        result=dict(job=job,prototype=True,release_evidence=False,converged=False)
        started=perf_counter()
        try:
            sol=flow.solve(tol=task.numerics.tolerance,max_iterations=args.budget,start=positions)
            result.update(converged=sol.convergence.converged,convergence=vars(sol.convergence))
            if sol.convergence.converged:
                seed=dict(z=sol.geometry.z,t=sol.geometry.y/sol.geometry.y[:,-1:])
                result.update(metrics=report_overall(sol,flow.gas,job['efficiency_temperature_basis']),positions=seed)
        except Exception as exc:result['failure']=getattr(exc,'diagnostics',{'message':str(exc)})
        result.update(elapsed_seconds=perf_counter()-started,trace=trace)
        write_json_new(output/(str(count)+'.json'),plain(result))
        print(count,result['converged'],result.get('failure',{}).get('message'),round(result['elapsed_seconds'],1),flush=True)


if __name__=='__main__':main()
