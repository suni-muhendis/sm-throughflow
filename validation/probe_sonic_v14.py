"""Conservative dual-cell passage-shock integration: research prototype."""
import argparse
import json
import numpy as np
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.phase3 import evaluate_job
from validation.probe_family_v14 import BASELINE
from sm_throughflow.correlations import aungier as A
from sm_throughflow.solver.aungier_row import AungierCompressorRow

def integrated_shock(mach,turn,head,mass,gamma,mean):
    x=np.r_[0.,np.cumsum(mass)];x/=x[-1]
    edges=np.r_[0.,.5*(x[1:]+x[:-1]),1.]
    nodes,weights=np.polynomial.legendre.leggauss(4)
    values=np.zeros_like(x)
    all_x=[];all_w=[];indices=[]
    for j,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
        knots=[lo,hi]+[v for v in x if lo<v<hi]
        for k in range(len(x)-1):
            if (mach[k]-1)*(mach[k+1]-1)<0:
                sonic=x[k]+(1-mach[k])*(x[k+1]-x[k])/(mach[k+1]-mach[k])
                if lo<sonic<hi:knots.append(sonic)
        knots=sorted(knots)
        for a,b in zip(knots[:-1],knots[1:]):
            all_x.extend(.5*(a+b)+.5*(b-a)*nodes);all_w.extend(.5*(b-a)*weights);indices.extend([j]*len(nodes))
    q=np.array(all_x)
    dp=A.shock_loss(np.interp(q,x,mach),np.interp(q,x,turn),gamma,mean)*np.interp(q,x,head)
    np.add.at(values,indices,dp*np.array(all_w))
    return values/np.diff(edges)/head

def main():
    p=argparse.ArgumentParser();p.add_argument('--id',default='original__nasa_stage53_100_2993');args=p.parse_args()
    original=AungierCompressorRow._inlet_part
    def part(self,inlet,geometry):
        d=original(self,inlet,geometry)
        d['omega_shock']=integrated_shock(d['mach1'],d['shock_flow_turning'],d['pt1']-inlet.P,inlet.tube_mass_flows,self.gas.gamma,self.shock_mean)
        return d
    AungierCompressorRow._inlet_part=part
    j=next(j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id']==args.id)
    out=create_campaign(purpose='v14_sonic_cell_integration_probe',selection=dict(release_evidence=False,prototype=True))
    r=evaluate_job(j);r.update(prototype=True,research_override='sonic_cell_integral',release_evidence=False)
    write_json_new(out/'result.json',r);print(out,r['classification'],r['metrics'],flush=True)

if __name__=='__main__':main()
