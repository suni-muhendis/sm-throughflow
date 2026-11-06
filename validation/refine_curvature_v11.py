"""Separate axial-grid continuation study, with an explicit 400-iteration budget.

Research initialization uses the public low-level solver's start positions.
It does not forge a high-level off-design restart key or alter the cold-start
policy used by the matched 108-job campaign. Failed levels remain recorded.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import json
from time import perf_counter
import numpy as np

from validation.campaign import create_campaign, write_json_new
from validation.compare_convergence_v11 import BASELINE
from validation.phase3 import plain, report_overall
from sm_throughflow.contracts import SIMULATOR_VERSION, AUNGIER_PROFILES, ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.errors import SolverError
from sm_throughflow.solver.verification import verify_solution
from sm_throughflow.solver.limits import solution_limits
from sm_throughflow.outcomes import failure_evidence


def sequence(jobs, output):
    seed = None
    for job in jobs:
        started = perf_counter()
        out = {k:v for k,v in job.items() if k not in ('design','task')}
        out.update(converged=False, metrics={}, seed_id=None if seed is None else seed['id'],
                   initialization='cold' if seed is None else 'interpolated_converged_coarser_grid')
        try:
            task = ThroughflowTaskV2.model_validate(job['task'])
            flow,_ = SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(job['design']),task,task.operating_points[0])
            positions = None if seed is None else np.column_stack([
                np.interp(flow.qn.z_hub,seed['z'][:,k],seed['t'][:,k]) for k in range(flow.n)])
            sol = flow.solve(tol=task.numerics.tolerance,max_iterations=task.numerics.max_iterations,
                             b_star=4.,start=positions)
            if not sol.convergence.converged:
                raise SolverError('axial refinement did not converge',component='outer',
                    iterations=sol.convergence.iterations,attempts=sol.convergence.attempts,
                    effort=sol.convergence.effort,residual=max(sol.convergence.velocity_change[-1],sol.convergence.position_change[-1]))
            balances = verify_solution(flow,sol,task.numerics.tolerance)
            low,high = AUNGIER_PROFILES[task.physics.physics_profile]['temperature_bounds_k']
            if min(np.min(st.T) for st in sol.stations)<low or max(np.max(st.T0) for st in sol.stations)>high:
                raise SolverError('temperature outside model scope',kind='outside_model_scope',component='gas')
            limits = solution_limits(sol)
            out.update(converged=True,classification='converged_with_model_limit' if limits['stall_criterion_crossed'] or limits['throat_capacity_exceeded'] else 'converged',
                       metrics=report_overall(sol,flow.gas,job['efficiency_temperature_basis']),
                       diagnostics=dict(verification=balances,limits=limits,convergence=vars(sol.convergence)))
            seed=dict(id=job['id'],z=sol.geometry.z,t=sol.geometry.y/sol.geometry.y[:,-1:])
            out['positions']=dict(z=seed['z'],t=seed['t'])
        except Exception as exc:
            out['diagnostics']=failure_evidence(exc)
            out['classification']=out['diagnostics']['classification']
        out['elapsed_seconds']=perf_counter()-started
        write_json_new(output/'results'/(job['id']+'.json'),plain(out))
        print(job['id'],out['classification'],round(out['elapsed_seconds'],1),flush=True)


def main():
    if SIMULATOR_VERSION!='slc_aungier_experimental_v11':raise ValueError('v11 required')
    jobs=[]
    for source in json.loads((BASELINE/'jobs.json').read_text()):
        if source['selection_id']!='nasa_stage35_100_3978':continue
        for count in (1,2,4,8):
            j=deepcopy(source)
            j.update(id=source['id']+'__axial_'+str(count),reference_id=source['id'],group='axial_refinement',
                     parameter='duct_subdivisions',value=count,release_evidence=False)
            j['task']['simulator_version']=SIMULATOR_VERSION
            j['task']['numerics'].update(duct_subdivisions=count,max_iterations=400)
            jobs.append(j)
    assert len(jobs)==8
    output=create_campaign(purpose='v11_separate_axial_continuation_study',selection=dict(
        jobs=8,duct_subdivisions=[1,2,4,8],outer_iterations_per_attempt=400,tolerance=1e-7,
        low_level_research_initialization=True,production_cold_start_policy_unchanged=True,release_evidence=False))
    write_json_new(output/'jobs.json',jobs)
    print(output,flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        for result in as_completed([pool.submit(sequence,[j for j in jobs if j['representation']==rep],output)
                                    for rep in ('projected','original')]):result.result()
    print('COMPLETE',output,flush=True)


if __name__=='__main__':main()
