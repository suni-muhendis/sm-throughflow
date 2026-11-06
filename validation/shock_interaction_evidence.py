"""Separate measured loss-budget evidence from v16 closure diagnostics.

The normal-shock pressure threshold is a historical turbulent interaction
indicator, not a universal separation classifier or a blockage correlation.
No printed data enter a simulator coefficient or a family-specific fit.
"""
import csv
import json
import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.probe_compressible_diffusion import BASELINE
from validation.screen_candidate_v16 import ANCHORS
from sm_throughflow.correlations import aungier as A


def measured_rows():
    path=ROOT/'validation/cases/nasa_rotor37_shock_interaction/TM107310_table7.csv'
    with path.open(encoding='utf-8',newline='') as stream:
        reader=csv.reader(stream)
        header,units=next(reader),next(reader)
        previous=None
        rows=[]
        for row in reader:
            expanded=[previous[i] if v=='"' else v for i,v in enumerate(row)]
            values={key: value if key=='Flow' else float(value) for key,value in zip(header,expanded)}
            rows.append(values)
            previous=expanded
    return rows


def main():
    rows=measured_rows()
    with (ROOT/'validation/cases/nasa_rotor37_shock_interaction/TM107310_table6.csv').open(encoding='utf-8',newline='') as stream:
        table=csv.reader(stream)
        headings=next(table)
        next(table)
        blockage=[dict(zip(headings,row)) for row in table]
    out=create_campaign(purpose='shock_viscous_interaction_source_evidence',selection=dict(
        release_evidence=False, qualification=False, baseline=BASELINE.name,
        source='NASA TM-107310, Tables 6-7 and printed pp. 183, 195-196, 200',
        limitation='Same Rotor 37 family; shock/profile split is estimated; blockage is a region-specific radial average'))
    experiment=[]
    for r in rows:
        mn=r['M₁']*np.sin(np.radians(r['β']))
        experiment.append(dict(r, normal_mach_from_printed_angle=float(mn),
            normal_mach_rounding_residual=float(mn-r['Mₙ']),
            loss_budget_rounding_residual=r['ω_total']-r['ω_shock']-r['ω_profile'],
            local_total_pressure_ratio=float(A.normal_shock_total_pressure_ratio(mn)),
            shock_static_pressure_ratio=float(1.+2.*1.4/2.4*(mn*mn-1.))))
    diagnostics={}
    for n,rd in ANCHORS.items():
        data=json.loads((BASELINE/f'results/original__nasa_stage{n}_100_{rd}.json').read_text())['row_diagnostics']['R1']
        mach=np.array(data['relative_inlet_mach'])
        ms=A.mach_from_prandtl_meyer_angle(A.prandtl_meyer_angle(mach)+np.maximum(data['shock_flow_turning'],0.))
        mn=.5*(mach+ms)
        pressure=1.+2.*1.4/2.4*(mn*mn-1.)
        diagnostics[str(n)]=dict(
            assumed_normal_mach=mn.tolist(), shock_pressure_ratio=pressure.tolist(),
            equivalent_diffusion=data['equivalent_diffusion'], wake_blockage=data['wake_blockage'],
            # Interior span points only; they are predictions, not experimental samples.
            interior_strong_shock_zero_wake_count=int(np.count_nonzero((pressure[1:-1]>1.89)&(np.array(data['wake_blockage'][1:-1])==0.))),
            separation_label=None, blockage_prediction_from_shock=None)
    comparison=dict(experimental_rows=experiment, experimental_blockage_table=blockage, v16_diagnostics=diagnostics,
        interpretation='A shock-only loss addition or Mach-only interaction multiplier cannot resolve the measured profile-loss dependence. Shock position, post-shock pressure gradient and boundary-layer state remain required.',
        caution='Pressure ratio 1.89 is an indicator from turbulent interaction literature, not sufficient evidence that a particular compressor section is separated. No universal separation/stall labels are assigned.',
        data_used_for_fitting=False, experimentally_qualified=False, training_label_qualified=False)
    write_json_new(out/'analysis.json',comparison)
    print(out,flush=True)


if __name__=='__main__':
    main()
