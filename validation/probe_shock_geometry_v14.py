"""Research-only metric-consistent shock foot, no table-target fitting."""
import argparse
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job
from sm_throughflow.simulator import SlcAungierSimulator as S
from sm_throughflow.correlations import blade_geometry as G

BASELINE=ROOT/'validation/campaigns/20261104T232522087684Z_slc_aungier_experimental_v13'

def metric_angles(row, stations):
    if row.profile not in ('dca','mca'):return None
    z=[s.axial_m for s in stations]
    zi,zo=row.leading_edge_axial_m,row.trailing_edge_axial_m
    hi,ho=np.interp([zi,zo],z,[s.hub_radius_m for s in stations])
    ti,to=np.interp([zi,zo],z,[s.shroud_radius_m for s in stations])
    angles=[]
    for s in S._sections(row,stations):
        span=s['span_fraction'];cp=np.cos(np.arctan2(ho+span*(to-ho)-hi-span*(ti-hi),zo-zi))
        upper,_,_=G.section(row.profile,row.camberline,s['camber'],s['t_c'],row.max_camber_location,row.edge_radius_to_chord,**s['shape'])
        p=G._stagger(upper,s['stagger'])
        delta=p-np.array([0.,1/s['solidity']]);delta[:,0]/=cp
        k=np.argmin(np.sum(delta*delta,axis=1))
        a=np.degrees(np.unwrap(np.arctan2(np.gradient(p[:,1]),np.gradient(p[:,0]))))
        angles.append((a[0],a[k]))
    return dict(leading=[a[0] for a in angles],foot=[a[1] for a in angles])

def run(job):
    S.shock_surface_angles=staticmethod(metric_angles)
    r=evaluate_job(job);r.update(prototype=True,research_override='projected_surface_metric',release_evidence=False)
    return r

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');a=parser.parse_args()
    if not a.full:
        from validation.phase3 import V
        from validation.phase3_rows import measured_states,row_model,geometry_file
        from sm_throughflow.solver.rows import ExitGeometry
        for n,rd in [(35,'3978'),(36,'4272'),(37,'4182'),(38,'4120')]:
            c=V.CASES['nasa_stage'+str(n)]();p=next(x for x in c.measured_points(100) if x['reading']==rd)
            g=V.L.read_geometry(geometry_file(c.case_id,0));i,e,rs=measured_states(c.rotor_elements[rd],g,p['rpm'],p['mass_flow'])
            m=row_model(c.design,0,p['rpm']);old=m(i,e,ExitGeometry(e.t,e.y,e.r,e.z)).diagnostics
            S.shock_surface_angles=staticmethod(metric_angles);m=row_model(c.design,0,p['rpm']);new=m(i,e,ExitGeometry(e.t,e.y,e.r,e.z)).diagnostics
            print(n,old['shock_loss'][5],new['shock_loss'][5],new['shock_flow_turning'][5],flush=True)
        return
    ids=['original__nasa_stage'+str(n)+'_100_'+rd for n,rd in [(35,'3978'),(36,'4272'),(37,'4182'),(38,'4120'),(53,'2993')]]
    jobs=[j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in ids]
    out=create_campaign(purpose='v14_metric_shock_geometry_probe',selection=dict(prototype=True,release_evidence=False))
    print(out,flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            r=f.result();write_json_new(out/'results'/(r['id']+'.json'),r);print(r['id'],r['classification'],r['metrics'],flush=True)

if __name__=='__main__':main()
