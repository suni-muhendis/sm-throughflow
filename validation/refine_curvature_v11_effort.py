"""Explicit higher-budget axial study; never pooled with the 200/400-step sets."""
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.refine_curvature_v11 import sequence
from sm_throughflow.contracts import SIMULATOR_VERSION


if __name__ == '__main__':
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v11':raise ValueError('v11 required')
    source=ROOT/'validation/campaigns/20261104T220809961902Z_slc_aungier_experimental_v11'
    jobs=json.loads((source/'jobs.json').read_text())
    for job in jobs:
        job['task']['numerics']['max_iterations']=1000
    output=create_campaign(purpose='v11_separate_axial_continuation_effort_study',selection=dict(
        jobs=8,duct_subdivisions=[1,2,4,8],outer_iterations_per_attempt=1000,tolerance=1e-7,
        low_level_research_initialization=True,production_cold_start_policy_unchanged=True,
        reference_400_iteration_campaign=source.name,release_evidence=False))
    write_json_new(output/'jobs.json',jobs)
    print(output,flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        for result in as_completed([pool.submit(sequence,[j for j in jobs if j['representation']==rep],output)
                                    for rep in ('projected','original')]):result.result()
    print('COMPLETE',output,flush=True)
