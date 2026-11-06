"""Frozen-input coupled pilot for a source-based compressibility hypothesis."""
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import evaluate_job
from validation.compressible_diffusion_candidate import override, VERSION

BASELINE = ROOT/'validation/campaigns/20261105T124800167736Z_slc_aungier_experimental_v16'


def run(job):
    with override():
        result = evaluate_job(job)
    result.update(prototype=True, release_evidence=False, research_override=VERSION,
                  training_label_qualified=False)
    return result


def main():
    ids = ['original__nasa_stage'+str(n)+'_100_'+rd for n, rd in {35:'3978',36:'4272',37:'4182',38:'4120',53:'2993'}.items()]
    jobs = [j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in ids]
    out = create_campaign(purpose='compressible_diffusion_coupled_pilot', selection=dict(
        prototype=True, release_evidence=False, baseline=BASELINE.name, research_override=VERSION,
        limitation='Linearized compressibility in Aungier diffusion/loss/blockage; not an experimentally validated interaction model'))
    write_json_new(out/'jobs.json', jobs)
    print(out, flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(run,j) for j in jobs]):
            r = future.result()
            write_json_new(out/'results'/(r['id']+'.json'), r)
            print(r['id'], r['classification'], r['metrics'], flush=True)
    print('COMPLETE', out, flush=True)


if __name__ == '__main__':
    main()
