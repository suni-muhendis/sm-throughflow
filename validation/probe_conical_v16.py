"""Source-native geometry counterfactual on v15; no production qualification."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
import json
import numpy as np

from validation.campaign import ROOT,create_campaign,write_json_new
from validation.phase3 import V,evaluate_job,plain
from validation.phase3_rows import geometry_file,condition_result
from validation.conical_reference_v16 import shock_foot
from sm_throughflow.correlations import aungier as A
from sm_throughflow.solver.aungier_row import AungierCompressorRow
from sm_throughflow.solver.shock_integration import integrated_shock_loss
from sm_throughflow.contracts import SIMULATOR_VERSION

BASELINE=ROOT/'validation/campaigns/20261105T095546195498Z_slc_aungier_experimental_v15'
ANCHORS={35:'3978',36:'4272',37:'4182',38:'4120'}


def geometry(case):
    data=[]
    for index in (0,1):
        g=sorted(V.L.read_geometry(geometry_file(case,index)),key=lambda r:float(r['RI']))
        blades=V.L.LEWIS_STAGES[case]['blades'][index]
        radius=np.array([float(r['RI']) for r in g])
        values=[shock_foot(r,blades) for r in g]
        data.append(dict(span=(radius-radius[0])/(radius[-1]-radius[0]),sections=values))
    return data


@contextmanager
def override(data,mode):
    original=AungierCompressorRow._inlet_part
    def replacement(self,inlet,exit_geometry):
        part=original(self,inlet,exit_geometry)
        g=data[self.row_number-1]
        foot=np.interp(inlet.t,g['span'],[x[mode+'_foot_deg'] for x in g['sections']])
        expansion=part['beta1']-foot
        part['shock_flow_turning']=expansion
        part['pointwise_shock']=A.shock_loss(part['mach1'],expansion,self.gas.gamma,self.shock_mean)
        part['omega_shock']=integrated_shock_loss(part['mach1'],expansion,part['pt1']-inlet.P,
                                                inlet.tube_mass_flows,self.gas.gamma,self.shock_mean)
        part['shock_compression_clipped']=(part['mach1']>1)&(expansion<0)
        return part
    AungierCompressorRow._inlet_part=replacement
    try: yield
    finally: AungierCompressorRow._inlet_part=original


def run(job,mode,data):
    with override(data,mode):
        result=evaluate_job(job)
    result.update(id=job['id']+'__cone_'+mode,prototype=True,release_evidence=False,
                  research_override='source_native_cone_'+mode)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');args=p.parse_args()
    assert SIMULATOR_VERSION=='slc_aungier_experimental_v15'
    out=create_campaign(purpose='v16_source_cone_geometry_attribution',selection=dict(
        prototype=True,release_evidence=False,baseline=BASELINE.name,
        limitation='Source geometry counterfactual; source KTC is not a production input; cone edge circles intrinsic'))
    print(out,flush=True)
    data={f'nasa_stage{n}':geometry(f'nasa_stage{n}') for n in ANCHORS}
    write_json_new(out/'geometry.json',plain(data))
    if args.full:
        ids=[f'original__nasa_stage{n}_100_{rd}' for n,rd in ANCHORS.items()]
        jobs=[j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in ids]
        write_json_new(out/'jobs.json',jobs)
        with ProcessPoolExecutor(max_workers=3) as pool:
            for f in as_completed([pool.submit(run,j,mode,data[j['case']]) for j in jobs for mode in ('local','developed')]):
                result=f.result();write_json_new(out/'results'/(result['id']+'.json'),result)
                print(result['id'],result['classification'],result['metrics'],flush=True)
    rows=[]
    for n,rd in ANCHORS.items():
        case=V.CASES[f'nasa_stage{n}']();point=next(p for p in case.measured_points(100) if p['reading']==rd)
        for index in (0,1):
            for mode in ('baseline','local','developed'):
                if mode=='baseline': result=condition_result(case,100,point,index)
                else:
                    with override(data[case.case_id],mode):result=condition_result(case,100,point,index)
                result['research_override']=mode;rows.append(result)
                pts=[p for p in result['points'] if p['core']]
                print(n,index,mode,float(np.mean([p['predicted_loss'] for p in pts])),flush=True)
    write_json_new(out/'rows.json',rows)
    print('COMPLETE',out,flush=True)


if __name__=='__main__':main()
