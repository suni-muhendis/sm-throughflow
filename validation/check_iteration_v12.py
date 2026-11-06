"""Explicit production startup and recovered-point wall-resolution evidence."""
import json
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed
from validation.campaign import create_campaign, write_json_new
from validation.compare_convergence_v12 import BASELINE
from validation.phase3 import evaluate_job
from sm_throughflow.contracts import SIMULATOR_VERSION


def main():
    assert SIMULATOR_VERSION=='slc_aungier_experimental_v12'
    sources={j['id']:j for j in json.loads((BASELINE/'jobs.json').read_text())}
    jobs=[]
    for rep in ('projected','original'):
        j=deepcopy(sources[rep+'__nasa_stage35_100_3978'])
        j.update(reference_id=j['id'],id=j['id']+'__production_axial_8',group='production_grid_startup')
        j['task']['numerics']['duct_subdivisions']=8
        jobs.append(j)
    for count in (1,8,16,32):
        j=deepcopy(sources['projected__nasa_stage35_90_3979'])
        j.update(reference_id=j['id'],id=j['id']+'__wall_'+str(count),group='recovered_wall_resolution',value=count)
        j['task']['numerics']['endwall_subdivisions']=count
        jobs.append(j)
    for j in jobs:
        j['task']['simulator_version']=SIMULATOR_VERSION
        j['release_evidence']=False
    output=create_campaign(purpose='v12_production_initialization_and_recovered_wall_resolution',
        selection=dict(jobs=len(jobs),outer_iterations_per_attempt=200,release_evidence=False))
    write_json_new(output/'jobs.json',jobs)
    print(output,flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(evaluate_job,j) for j in jobs]):
            r=future.result()
            write_json_new(output/'results'/(r['id']+'.json'),r)
            print(r['id'],r['classification'],round(r['elapsed_seconds'],1),flush=True)
    print('COMPLETE',output,flush=True)


if __name__=='__main__':main()
