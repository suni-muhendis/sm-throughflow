"""Research-only coarse-to-fine starts with the explicit curvature override."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import argparse
import json
import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.probe_curvature_v11 import BASELINE, run
from sm_throughflow.contracts import SIMULATOR_VERSION, ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator

SEEDS = ROOT/'validation/campaigns/20261104T215514244640Z_slc_aungier_experimental_v10'


def sequence(rep, output, b_star):
    jobs=json.loads((BASELINE/'jobs.json').read_text())
    job=next(j for j in jobs if j['id']==rep+'__nasa_stage35_100_3978')
    seed=json.loads((SEEDS/(job['id']+'__quadratic.json')).read_text())
    source=str(SEEDS/(job['id']+'__quadratic.json'))
    assert seed['converged']
    for count in (2,4,8):
        j=deepcopy(job); j['id']+=f'__duct_{count}'
        j['task']['numerics']['duct_subdivisions']=count
        task=ThroughflowTaskV2.model_validate(j['task'])
        flow,_=SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(j['design']),task,task.operating_points[0])
        positions=np.column_stack([np.interp(flow.qn.z_hub, np.asarray(seed['last']['z'])[:,k],
                                           np.asarray(seed['last']['t'])[:,k]) for k in range(flow.n)])
        r=run(j,'quadratic',positions,b_star=b_star)
        r['seed_source']=source
        path=output/(r['id']+'.json');write_json_new(path,r)
        print(r['id'],r['converged'],r.get('failure'),r['elapsed_seconds'],flush=True)
        if r['converged']:seed,source=r,str(path)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--b-star', type=float, default=4.)
    args=parser.parse_args()
    if SIMULATOR_VERSION!='slc_aungier_experimental_v10':raise ValueError('Use archived v10 source')
    output=create_campaign(purpose='v11_coarse_to_fine_research_on_v10',selection=dict(
        prototype=True,geometry_override='quadratic',seed_campaign=SEEDS.name,b_star=args.b_star,duct_subdivisions=[2,4,8],release_evidence=False))
    print(output,flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        for result in as_completed([pool.submit(sequence,rep,output,args.b_star) for rep in ('projected','original')]):
            result.result()
