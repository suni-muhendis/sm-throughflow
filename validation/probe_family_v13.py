"""Explicit counterfactuals on frozen v12; not production or qualification evidence."""
import argparse
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job, V
from validation.phase3_rows import geometry_file
from sm_throughflow.simulator import SlcAungierSimulator as S
from sm_throughflow.correlations import aungier as A
from sm_throughflow.correlations import blade_geometry as G
from sm_throughflow.solver.aungier_row import AungierCompressorRow

BASELINE=ROOT/'validation/campaigns/20261104T225400132975Z_slc_aungier_experimental_v12'
ANCHORS=['nasa_stage35_100_3978','nasa_stage36_100_4272','nasa_stage37_100_4182','nasa_stage38_100_4120']
MODES=['baseline','no_shock','no_clearance','no_reynolds','no_endwall_profile','no_supercritical','no_incidence_profile','published_phi',
       'flow_angle_shock','flow_angle_shock_projected','conical_sections']


def run(job, mode):
    originals={k:getattr(A,k) for k in ('shock_loss','tip_clearance_loss','reynolds_loss_factor',
        'endwall_loss_constant','minimum_loss','off_design_loss')}
    expansion=S.expansion_angles
    sections=S._sections
    build, inlet_part=S.build,AungierCompressorRow._inlet_part
    if mode=='conical_sections':
        def cone_sections(row,stations):
            items=sections(row,stations)
            z=[s.axial_m for s in stations]
            zi,zo=row.leading_edge_axial_m,row.trailing_edge_axial_m
            hi,ho=np.interp([zi,zo],z,[s.hub_radius_m for s in stations])
            ti,to=np.interp([zi,zo],z,[s.shroud_radius_m for s in stations])
            for k,s in enumerate(items):
                t=s['span_fraction'];ri=hi+t*(ti-hi);ro=ho+t*(to-ho)
                cp=np.cos(np.arctan2(ro-ri,zo-zi))
                k1=abs(row.metal_angle_in_deg[k]);k2=abs(row.metal_angle_out_deg[k])
                k1,k2=np.degrees(np.arctan(cp*np.tan(np.radians([k1,k2]))))
                camber=k1-k2
                chi,ac=G.mca_shape(camber,s['shape']['transition'],s['shape']['turning_ratio'])
                s.update(camber=camber,stagger=k1-chi,chi1_over_camber=chi/camber,a_c=ac,
                         chord=s['chord']/cp,t_c=s['t_c']*cp,solidity=s['chord']/cp*row.blade_count/(np.pi*(ri+ro)))
            return items
        S._sections=staticmethod(cone_sections)
    if mode=='no_shock':A.shock_loss=lambda mach,*args,**kwargs:np.zeros_like(mach)
    if mode=='no_clearance':A.tip_clearance_loss=lambda pressure,*args,**kwargs:np.zeros_like(pressure)
    if mode=='no_reynolds':A.reynolds_loss_factor=lambda re:np.zeros_like(re)
    if mode=='no_endwall_profile':A.endwall_loss_constant=lambda pitch,beta,re,K1:1.+.004*re/K1
    if mode=='no_supercritical':
        A.minimum_loss=lambda omega,im,istar,Rs,*args,**kwargs:omega*(1+(im-istar)**2/Rs**2)
    if mode=='no_incidence_profile':A.off_design_loss=lambda i,im,ic,istall,minimum,shock:minimum+shock
    if mode=='published_phi':
        def source_phi(row,stations):
            index=0 if row.row_type=='rotor' else 1
            geom=sorted(V.L.read_geometry(geometry_file(job['case'],index)),key=lambda r:float(r['RI']))
            radii=np.array([.5*(float(r['RI'])+float(r['RO'])) for r in geom])
            span=(radii-radii[0])/(radii[-1]-radii[0])
            return np.interp(np.linspace(0,1,11),span,[float(r['PHISS']) for r in geom]).tolist()
        S.expansion_angles=staticmethod(source_phi)
    if mode.startswith('flow_angle_shock'):
        def with_surface_angles(design,task,point):
            flow,models=build(design,task,point)
            for row in design.rows:
                angles=[]
                for s in S._sections(row,design.passage.stations):
                    upper,_,_=G.section(row.profile,row.camberline,s['camber'],s['t_c'],row.max_camber_location,
                        row.edge_radius_to_chord,**s['shape'])
                    suction=G._stagger(upper,s['stagger'])
                    foot=np.argmin(np.hypot(*(suction-np.array([0.,1/s['solidity']])).T))
                    angle=np.unwrap(np.arctan2(np.gradient(suction[:,1]),np.gradient(suction[:,0])))
                    angles.append(float(np.degrees(angle[foot])))
                models[row.row_id]._research_shock_angles=angles
            return flow,models
        S.build=staticmethod(with_surface_angles)
        def incoming_direction(self,inlet,exit_geometry):
            part=inlet_part(self,inlet,exit_geometry)
            foot=np.interp(inlet.t,np.linspace(0,1,11),self._research_shock_angles)
            if mode.endswith('_projected'):
                phi=np.arctan2(exit_geometry.r-inlet.r,exit_geometry.z-inlet.z)
                foot=np.degrees(np.arctan(np.cos(phi)*np.tan(np.radians(foot))))
            part['omega_shock']=originals['shock_loss'](part['mach1'],part['beta1']-foot,self.gas.gamma,self.shock_mean)
            return part
        AungierCompressorRow._inlet_part=incoming_direction
    try:
        result=evaluate_job(job)
        result.update(id=job['id']+'__'+mode,research_override=mode,prototype=True,
                      release_evidence=False,interpretation='Counterfactual attribution, not a calibrated production model')
        return result
    finally:
        for key,value in originals.items():setattr(A,key,value)
        S.expansion_angles=staticmethod(expansion)
        S._sections=staticmethod(sections)
        S.build=staticmethod(build)
        AungierCompressorRow._inlet_part=inlet_part


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--modes',nargs='+',default=MODES,choices=MODES)
    args=parser.parse_args()
    assert S.VERSION=='slc_aungier_experimental_v12','Use archived v12 source'
    jobs=[j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in ['original__'+a for a in ANCHORS]]
    output=create_campaign(purpose='v13_family_counterfactuals_on_frozen_v12',selection=dict(
        baseline=BASELINE.name,ids=[j['id'] for j in jobs],modes=args.modes,prototype=True,release_evidence=False))
    write_json_new(output/'jobs.json',jobs)
    print(output,flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(run,j,mode) for j in jobs for mode in args.modes]):
            r=future.result()
            write_json_new(output/'results'/(r['id']+'.json'),r)
            print(r['id'],r['classification'],r['metrics'].get('stage_eta'),round(r['elapsed_seconds'],1),flush=True)
    print('COMPLETE',output,flush=True)


if __name__=='__main__':main()
