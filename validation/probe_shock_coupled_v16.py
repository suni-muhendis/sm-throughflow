"""Coupled pilot for an unqualified Schobeiri meanline extension."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import json
from validation.probe_shock_v16 import geometry,override,ANCHORS
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.phase3 import evaluate_job
from sm_throughflow.contracts import SIMULATOR_VERSION

BASELINE=ROOT/'validation/campaigns/20261105T095546195498Z_slc_aungier_experimental_v15'


def run(job):
    with override(geometry(job['design']),True,None):
        result=evaluate_job(job)
    result.update(prototype=True,release_evidence=False,research_override='schobeiri_meanline_mca_nodewise')
    return result


def main():
    assert SIMULATOR_VERSION=='slc_aungier_experimental_v15'
    ids=[f'original__nasa_stage{n}_100_{rd}' for n,rd in ANCHORS.items()]
    jobs=[j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in ids]
    out=create_campaign(purpose='v16_schobeiri_coupled_pilot',selection=dict(
        prototype=True,release_evidence=False,baseline=BASELINE.name,
        limitation='Unqualified generalization; nodewise, no sonic-cell integration'))
    write_json_new(out/'jobs.json',jobs);print(out,flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(run,j) for j in jobs]):
            result=future.result();write_json_new(out/'results'/(result['id']+'.json'),result)
            print(result['id'],result['classification'],result['metrics'],flush=True)
    print('COMPLETE',out,flush=True)


if __name__=='__main__':main()
