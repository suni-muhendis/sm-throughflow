"""Existence diagnostic from an archived solution, never production initialization."""
import json
import numpy as np
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.phase3 import evaluate_job
from sm_throughflow.solver import throughflow as T

def main():
    old=ROOT/'validation/campaigns/20261104T225400132975Z_slc_aungier_experimental_v12'
    base=ROOT/'validation/campaigns/20261104T232522087684Z_slc_aungier_experimental_v13'
    key='original__nasa_stage53_100_2993'
    job=next(j for j in json.loads((base/'jobs.json').read_text()) if j['id']==key)
    states=json.loads((old/'results'/(key+'.json')).read_text())['stations']
    start=np.array([s['t'] for s in states])
    original=T.Throughflow.solve
    def warm(self,**kwargs):
        kwargs['start']=start
        return original(self,**kwargs)
    T.Throughflow.solve=warm
    out=create_campaign(purpose='v14_archived_seed_existence_probe',selection=dict(release_evidence=False,prototype=True))
    r=evaluate_job(job);r.update(prototype=True,research_override='archived_v12_seed',release_evidence=False)
    write_json_new(out/'result.json',r);print(out,r['classification'],r['metrics'],flush=True)

if __name__=='__main__':main()
