"""Explicit research overrides on frozen v10; never standard v10 evidence."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import json
from time import perf_counter

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import plain, report_overall
from sm_throughflow.contracts import SIMULATOR_VERSION, ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.verification import verify_solution
import sm_throughflow.solver.geometry as geometry

BASELINE = ROOT/'validation/campaigns/20261104T203655068245Z_slc_aungier_experimental_v10'


def quadratic_geometry(z, r):
    """Three-point parametric quadratic derivative, with one-sided end fits."""
    h = np.hypot(np.diff(z, axis=0), np.diff(r, axis=0))
    m = np.vstack([np.zeros((1, z.shape[1])), np.cumsum(h, axis=0)])
    if len(z) < 3:
        phi = np.broadcast_to(np.arctan2(r[-1]-r[0], z[-1]-z[0]), z.shape).copy()
        return m, phi, np.zeros_like(z)
    phi, kappa = np.empty_like(z), np.empty_like(z)
    for j in range(z.shape[1]):
        dz, dr = (np.gradient(v[:, j], m[:, j], edge_order=2) for v in (z, r))
        ddz, ddr = (2*np.diff(np.diff(v[:, j])/h[:, j])/(h[:-1, j]+h[1:, j]) for v in (z, r))
        ddz, ddr = (np.r_[v[0], v, v[-1]] for v in (ddz, ddr))
        phi[:, j] = np.arctan2(dr, dz)
        kappa[:, j] = -(dz*ddr-dr*ddz)/(dz*dz+dr*dr)**1.5
    return m, phi, kappa


def run(job, mode, start_positions=None, b_star=16.):
    start = perf_counter()
    old_geometry = geometry._slope_and_curvature
    if mode == 'quadratic':
        geometry._slope_and_curvature = quadratic_geometry
    task = ThroughflowTaskV2.model_validate(job['task'])
    flow, _ = SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(job['design']), task, task.operating_points[0])
    trace, last = [], {}
    original = flow._coupled_iteration
    def measured(*args):
        try:
            result = original(*args)
        except Exception as exc:
            trace.append(dict(evaluation=flow._effort['outer_iterations'], failure=getattr(exc, 'diagnostics', {'message':str(exc)})))
            raise
        geo, states, perf, wall, kb, target, move, field, blockage, mixing = result
        t = args[0]
        index = np.unravel_index(np.argmax(np.abs(target-t)), t.shape)
        trace.append(dict(evaluation=flow._effort['outer_iterations'], move=move, field=field,
                          blockage=blockage, mixing=mixing, worst_position=index,
                          max_curvature=float(np.max(np.abs(geo.kappa))),
                          damping_min=float(np.min(flow._damping(geo,states,b_star)))))
        last.update(t=t.copy(), target=target.copy(), kappa=geo.kappa, z=geo.z, r=geo.r,
                    phi=geo.phi, kb=flow._kb.copy(), wall_corrections=list(flow.endwall._delta_nu.items()))
        return result
    flow._coupled_iteration = measured
    result = dict(id=job['id']+'__'+mode, prototype=True, geometry_override=mode,
                  job=deepcopy(job), converged=False, release_evidence=False,
                  start_positions=start_positions, b_star=b_star)
    try:
        sol = flow._solve(task.numerics.tolerance, task.numerics.max_iterations, b_star,
                          t_start=start_positions, method='anderson')
        result.update(converged=sol.convergence.converged, convergence=vars(sol.convergence))
        if sol.convergence.converged:
            result.update(verification=verify_solution(flow, sol, task.numerics.tolerance),
                          metrics=report_overall(sol, flow.gas, job['efficiency_temperature_basis']))
    except Exception as exc:
        result['failure'] = getattr(exc, 'diagnostics', {'message':str(exc)})
    finally:
        geometry._slope_and_curvature = old_geometry
    result.update(trace=trace, last=last, elapsed_seconds=perf_counter()-start)
    return plain(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modes', nargs='+', default=['baseline','quadratic'], choices=['baseline','quadratic'])
    parser.add_argument('--ids', nargs='+', default=['projected__nasa_stage35_100_3978','original__nasa_stage35_100_3978','original__anchor_duct_subdivisions_4'])
    args = parser.parse_args()
    if SIMULATOR_VERSION != 'slc_aungier_experimental_v10':
        raise ValueError('Replay from the archived v10 source')
    jobs = [j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id'] in args.ids]
    if {j['id'] for j in jobs} != set(args.ids):
        raise ValueError('Unknown job')
    output = create_campaign(purpose='v11_curvature_research_on_v10', selection=dict(
        prototype=True, modes=args.modes, ids=args.ids, cold_anderson_only=True, release_evidence=False))
    print(output, flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(run,j,m) for j in jobs for m in args.modes]):
            r=future.result()
            write_json_new(output/(r['id']+'.json'),r)
            print(r['id'],r['converged'],r.get('failure'),r['elapsed_seconds'],flush=True)


if __name__ == '__main__':
    main()
