"""Conditioned-state shock-closure attribution; never production evidence."""
from contextlib import contextmanager
import numpy as np
from validation.campaign import create_campaign, write_json_new
from validation.phase3 import V, plain, Simulator
from validation.phase3_rows import condition_result
from validation.shock_reference_v16 import shock, circular_arc
from sm_throughflow.correlations.blade_geometry import camberline, _stagger, _arc_length
from sm_throughflow.contracts import ThroughflowDesignV2, SIMULATOR_VERSION
from sm_throughflow.solver.aungier_row import AungierCompressorRow
from sm_throughflow.solver.errors import SolverError

ANCHORS={35:'3978',36:'4272',37:'4182',38:'4120'}


def geometry(design):
    design=ThroughflowDesignV2.model_validate(design)
    rows=[]
    for row in design.rows:
        curves=[]
        for sec in Simulator._sections(row,design.passage.stations):
            kw={k:v for k,v in sec['shape'].items() if k in ('transition','turning_ratio')}
            x,y=camberline(row.camberline,sec['camber'],row.max_camber_location,**kw)
            p=_stagger(np.column_stack((x,y)),sec['stagger'])*sec['solidity']
            a=_arc_length(p[:,0],p[:,1])
            curves.append(np.column_stack([np.interp(np.linspace(0,1,401),a,p[:,j]) for j in (0,1)]))
        rows.append(np.array(curves))
    return rows


@contextmanager
def override(curves,height,record):
    original=AungierCompressorRow._inlet_part
    def replacement(self,inlet,exit_geometry):
        part=original(self,inlet,exit_geometry)
        if self.camberline != 'multiple_circular_arc':
            return part
        curve=curves[self.row_number-1]
        t=np.clip(inlet.t,0.,1.)*(len(curve)-1)
        low=np.minimum(t.astype(int),len(curve)-2);w=(t-low)[:,None,None]
        p=(1-w)*curve[low]+w*curve[low+1]
        cp=np.cos(np.arctan2(exit_geometry.r-inlet.r,exit_geometry.z-inlet.z))
        p[:,:,0]/=cp[:,None]
        hr=exit_geometry.y[-1]/inlet.y[-1] if height else 1.
        values=[shock(m,b,c,hr,self.gas.gamma) for m,b,c in zip(part['mach1'],part['beta1'],p)]
        if record is not None: record.append(dict(row=self.row_number,points=values))
        if any(v['loss'] is None for v in values):
            raise SolverError('research shock closure lacks a unique admissible root',kind='outside_model_scope',component='shock_reference')
        part['omega_shock']=np.array([v['loss'] for v in values])
        part['pointwise_shock']=part['omega_shock'].copy()
        part['shock_flow_turning']=np.array([v['roots'][0]['expansion_deg'] if v['roots'] else 0. for v in values])
        part['shock_compression_clipped']=np.zeros_like(part['mach1'],dtype=bool)
        return part
    AungierCompressorRow._inlet_part=replacement
    try:yield
    finally:AungierCompressorRow._inlet_part=original


def main():
    assert SIMULATOR_VERSION=='slc_aungier_experimental_v15'
    out=create_campaign(purpose='v16_schobeiri_conditioned_attribution',selection=dict(
        prototype=True,release_evidence=False,source='10.1155/S1023621X9700016X',
        limitation='Planar sharp-edge meanline extension; conditioned rows only; no span-cell integration'))
    print(out,flush=True)
    # Source p. 173 quotes approximately 9.5 deg for M1=1.2, S/R=.5, beta_t=30deg.
    ref=shock(1.2,60.,circular_arc(60.,2.,45.))
    write_json_new(out/'reference.json',plain(ref));print('REFERENCE',ref,flush=True)
    results=[]
    for n,rd in ANCHORS.items():
        case=V.CASES[f'nasa_stage{n}']();point=next(p for p in case.measured_points(100) if p['reading']==rd)
        curves=geometry(case.design)
        for index in (0,1):
            for mode in ('baseline','constant_height','contracting_height'):
                record=[]
                try:
                    if mode=='baseline':result=condition_result(case,100,point,index)
                    else:
                        with override(curves,mode=='contracting_height',record):result=condition_result(case,100,point,index)
                    pts=[p for p in result['points'] if p['core']]
                    mean=float(np.mean([p['predicted_loss'] for p in pts]))
                except Exception as exc:
                    result=dict(error=type(exc).__name__+': '+str(exc));mean=None
                result.update(stage=n,index=index,research_override=mode,shock_reference=record)
                results.append(result);print(n,index,mode,mean,flush=True)
    write_json_new(out/'rows.json',plain(results));print('COMPLETE',out,flush=True)


if __name__=='__main__':main()
