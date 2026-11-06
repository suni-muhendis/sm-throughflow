"""Nodewise coupled feasibility pilot; explicitly not a production closure.

Only the supersonic MCA shock term changes. The v16 subsonic empirical
correction, viscous profile loss and wake closure remain as background.
This isolates missing branch/back-pressure physics; it does not supply a
consistent interaction closure or preserve sonic-cell integration.
"""
from contextlib import contextmanager
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import numpy as np

from validation.campaign import create_campaign, write_json_new
from validation.phase3 import evaluate_job
from validation.probe_compressible_diffusion import BASELINE
from validation.probe_passage_shock import pressure_contours, surfaces, ANCHORS
from validation.passage_shock_candidate import shock, unchoked
from sm_throughflow.solver.aungier_row import AungierCompressorRow, smooth_loss
from sm_throughflow.solver.rows import RowPerformance
from sm_throughflow.solver.errors import SolverError

VERSION='passage_shock_backpressure_nodewise_r2'
MAX_ROW_EVALUATIONS=1000


@contextmanager
def override(design):
    original=AungierCompressorRow.__call__
    geometries={i+1:pressure_contours(design,i) for i,row in enumerate(design['rows']) if row['profile']=='mca'}
    cached={}
    calls=0
    def replacement(self,inlet,exit,geometry):
        nonlocal calls
        calls+=1
        if calls>MAX_ROW_EVALUATIONS:
            raise SolverError('research passage-shock row-evaluation budget exhausted',
                kind='numerical_failure',component='research_passage_shock_budget',
                iterations=calls,details=dict(max_row_evaluations=MAX_ROW_EVALUATIONS,
                                             research_override=VERSION,physical_limit_proven=False))
        base=original(self,inlet,exit,geometry)
        if self.row_number not in geometries:
            return base
        previous=cached.get(self)
        if previous is not None and previous[0] is inlet and previous[1] is geometry:
            fields,part=previous[2:]
        else:
            fields,part=surfaces(self,inlet,geometry,*geometries[self.row_number])
            cached[self]=(inlet,geometry,fields,part)
        values=[]
        loss=[]
        for i,surface in enumerate(fields):
            m,b=part['mach1'][i],part['beta1'][i]
            if m<=1.:
                value=dict(loss=0.,regime='v16_subsonic_background')
            else:
                try:
                    if exit is None:
                        value=unchoked(m,max(b,surface.choke_angle(m)),surface,self.gas.gamma)
                    else:
                        value=shock(m,b,abs(np.degrees(base.exit_angle[i])),exit.P[i]/part['pt1'][i],surface,self.gas.gamma)
                except ValueError as exc:
                    raise SolverError('research passage-shock iterate unsupported: '+str(exc),
                        kind='outside_model_scope',component='research_passage_shock',
                        details=dict(research_override=VERSION,span_index=i,mach=float(m),angle=float(b),
                                     physical_limit_proven=False)) from exc
            values.append(value['regime'])
            loss.append(value['loss'])
        d=dict(base.diagnostics)
        new_shock=np.array(loss)
        head=part['pt1']-inlet.P
        profile=d['profile_loss']-d['shock_loss']+new_shock
        unlimited=profile+d['clearance_loss']+d['seal_loss']
        limited=np.minimum(unlimited,self.max_loss)
        output=smooth_loss(limited*head)/head if self.smoothing else limited
        d.update(shock_loss=new_shock,pointwise_shock_loss=new_shock,profile_loss=profile,loss=output,
                 loss_limit_active=unlimited>self.max_loss,unsmoothed_loss=limited,research_regimes=values,
                 research_shock_viscous_coupling_complete=False)
        return RowPerformance(base.exit_angle,output,base.basis,base.wake_blockage,d)
    AungierCompressorRow.__call__=replacement
    try:
        yield
    finally:
        AungierCompressorRow.__call__=original


def run(job):
    with override(job['design']):
        result=evaluate_job(job)
    result.update(prototype=True,release_evidence=False,research_override=VERSION,training_label_qualified=False)
    return result


def main():
    ids=[f'original__nasa_stage{n}_100_{rd}' for n,rd in ANCHORS.items()]
    ids.append('original__nasa_stage53_100_2993')
    jobs=[j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in ids]
    out=create_campaign(purpose='passage_shock_coupled_feasibility',selection=dict(
        prototype=True,release_evidence=False,research_override=VERSION,baseline=BASELINE.name,
        max_row_evaluations=MAX_ROW_EVALUATIONS,
        limitation='Nodewise shock-only hybrid, no AVDR or viscous coupling; no physical-limit proof from failed iterates'))
    write_json_new(out/'jobs.json',jobs)
    print(out,flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(run,j) for j in jobs]):
            r=future.result()
            write_json_new(out/'results'/(r['id']+'.json'),r)
            print(r['id'],r['classification'],r['metrics'],flush=True)
    print('COMPLETE',out,flush=True)


if __name__=='__main__':
    main()
