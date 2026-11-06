"""Separate wall-march resolution study; never pooled with the 108 fixed jobs."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import json

from validation.compare_convergence_v12 import BASELINE
from validation.campaign import create_campaign, write_json_new
from validation.phase3 import evaluate_job
from sm_throughflow.contracts import SIMULATOR_VERSION


def main():
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v12':
        raise ValueError('v12 required')
    jobs = []
    for source in json.loads((BASELINE/'jobs.json').read_text()):
        if source['id'] not in ('original__nasa_stage35_100_3978', 'original__nasa_stage38_90_4133'):
            continue
        for count in (16, 32):
            job = deepcopy(source)
            job.update(id=source['id']+'__wall_'+str(count), reference_id=source['id'],
                       group='endwall_refinement', parameter='endwall_subdivisions', value=count)
            job['task']['simulator_version'] = SIMULATOR_VERSION
            job['task']['numerics']['endwall_subdivisions'] = count
            jobs.append(job)
    output = create_campaign(purpose='v12_wall_march_refinement', selection=dict(jobs=4, subdivisions=[16, 32],
        reference_subdivisions=8, release_evidence=False))
    write_json_new(output/'jobs.json', jobs)
    print(output, flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(evaluate_job, j) for j in jobs]):
            result = future.result()
            write_json_new(output/'results'/(result['id']+'.json'), result)
            print(result['id'], result['classification'], round(result['elapsed_seconds'], 1), flush=True)
    print('COMPLETE', output, flush=True)


if __name__ == '__main__':
    main()
