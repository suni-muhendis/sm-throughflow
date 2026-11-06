"""Independent modal checks and regressions for captured v11 failures."""
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from sm_throughflow.contracts import SIMULATOR_VERSION, ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.reposition import elliptic_position_step
from sm_throughflow.solver.errors import SolverError
from sm_throughflow.solver.endwall import EndwallBoundaryLayers, _Edge, WallState

FIXTURES = Path(__file__).parent/'fixtures'


@pytest.mark.parametrize('nq, mode', [(17, 1), (33, 1), (33, 31), (65, 63)])
def test_elliptic_inverse_cancels_known_axial_radial_mode(nq, mode):
    ns, length, height, mach = 21, .3, .1, .2
    axial = np.linspace(0., length, nq)
    radial = np.linspace(0., height, ns)
    geo = SimpleNamespace(y=np.tile(radial, (nq, 1)), m=np.tile(axial[:, None], (1, ns)))
    stations = [SimpleNamespace(Wm=np.full(ns, mach), a=np.ones(ns)) for _ in axial]
    error = np.sin(mode*np.pi*axial/length)[:, None]*np.sin(np.pi*radial/height)
    error[[0,-1], :], error[:, [0,-1]] = 0., 0.
    ky = 4*np.sin(np.pi/(2*(ns-1)))**2/(height/(ns-1))**2
    km = (1-mach**2)*4*np.sin(mode*np.pi/(2*(nq-1)))**2/(length/(nq-1))**2
    residual = -(1+km/ky)*error
    np.testing.assert_allclose(elliptic_position_step(geo, stations, residual), -error, atol=2e-12)
    np.testing.assert_array_equal(elliptic_position_step(geo, stations, np.zeros_like(error)), 0.)


def test_captured_3979_duct_residual_requires_wall_substeps():
    values = json.loads((FIXTURES/'v11_stage35_3979_duct_gap.json').read_text())['inputs']
    e1,e2 = [_Edge(**values[name]) for name in ('e1','e2')]
    initial = WallState(**values['s1'])
    def run(count):
        wall=EndwallBoundaryLayers(max_passes=200,subdivisions=count)
        return wall._integrate_gap(e1,e2,initial,values['initial'],values['omega_w'],None,
                                   ('captured','hub'),'hub',values['station'])
    with pytest.raises(SolverError) as failure:
        run(1)
    assert failure.value.diagnostics['kind']=='numerical_failure'
    assert failure.value.diagnostics['residual']>.02
    states=[]
    for count in (8,16,32):
        state,nu,diagnostics=run(count)
        assert nu==0. and state.theta11>0 and state.delta1>0
        assert len(diagnostics)==count
        assert all(d['residual']<=1e-8 and d['iterations']<=200 for d in diagnostics)
        states.append(state.theta11)
    assert abs(states[1]-states[2]) < abs(states[0]-states[1])
    assert run(8)==run(8)


def test_elliptic_manufactured_polynomial_on_stretched_grids_is_second_order():
    # Independent continuous solution: -u'' = y(H-y), u(0)=u(H)=0.
    # For e=z(L-z)y(H-y), (I+Ky^-1 Km)e=e+2(1-M^2)u.
    errors=[]
    for n in (17,33,65):
        length,height,mach=.3,.1,.2
        z=length*np.linspace(0,1,n)**1.3
        y=height*np.linspace(0,1,n)**1.3
        geo=SimpleNamespace(y=np.tile(y,(n,1)),m=np.tile(z[:,None],(1,n)))
        stations=[SimpleNamespace(Wm=np.full(n,mach),a=np.ones(n)) for _ in z]
        expected=(z*(length-z))[:,None]*(y*(height-y))[None,:]
        u=height**3*y/12-height*y**3/6+y**4/12
        residual=expected+2*(1-mach**2)*u[None,:]
        residual[[0,-1],:]=0.
        residual[:,[0,-1]]=0.
        actual=elliptic_position_step(geo,stations,residual)
        errors.append(np.max(np.abs(actual-expected))/np.max(expected))
        np.testing.assert_array_equal(actual[:,[0,-1]],0.)
    assert errors[0]/errors[1]>3.5 and errors[1]/errors[2]>3.5


def machine(identifier, subdivisions=1):
    jobs=json.loads((FIXTURES/'v11_stage35_iteration_jobs.json').read_text())['jobs']
    job=next(j for j in jobs if j['id']==identifier)
    job['task']['simulator_version']=SIMULATOR_VERSION
    job['task']['numerics']['duct_subdivisions']=subdivisions
    task=ThroughflowTaskV2.model_validate(job['task'])
    return ThroughflowDesignV2.model_validate(job['design']),task,task.operating_points[0]


@pytest.mark.parametrize('representation',['original','projected'])
def test_stage35_eightfold_grid_converges_with_accounted_production_startup(representation):
    design,task,point=machine(representation+'__nasa_stage35_100_3978',8)
    flow,_,solution,balances,_=SlcAungierSimulator.solve_state(design,task,point)
    conv=solution.convergence
    assert conv.converged and conv.iterations<200
    assert max(conv.position_change[-1],conv.velocity_change[-1])<=task.numerics.tolerance
    attempts=conv.attempts
    assert not attempts[0]['converged'] and attempts[0]['grid_role']=='requested_initial'
    assert {a['duct_subdivisions'] for a in attempts if a['grid_role']=='coarse_seed'}=={1,2,4}
    assert attempts[-1]['grid_role']=='requested_retry' and attempts[-1]['duct_subdivisions']==8
    for key in conv.effort:
        assert conv.effort[key]==sum(a.get('effort',{}).get(key,0) for a in attempts)
    assert conv.effort['outer_iterations']>conv.iterations
    assert balances['mass_relative_error']<1e-9
    assert all(d['residual']<=1e-8 for d in solution.endwall.convergence)


def test_regressed_3979_is_repeatable_and_respects_unchanged_residuals():
    args=machine('projected__nasa_stage35_90_3979')
    first=SlcAungierSimulator.solve_state(*args)[2]
    second=SlcAungierSimulator.solve_state(*args)[2]
    assert first.convergence==second.convergence
    assert first.convergence.converged
    assert max(first.convergence.position_change[-1],first.convergence.velocity_change[-1])<=1e-7
    for a,b in zip(first.stations,second.stations):
        np.testing.assert_array_equal(a.P0,b.P0)
        np.testing.assert_array_equal(a.Wm,b.Wm)


def test_proven_inlet_capacity_does_not_trigger_coarse_grid_retries():
    design,task,point=machine('original__nasa_stage35_100_3978',8)
    point.mass_flow_kg_s=1e6
    with pytest.raises(SolverError) as failure:
        SlcAungierSimulator.solve_state(design,task,point)
    evidence=failure.value.diagnostics
    assert evidence['kind']=='physical_capacity_exceeded'
    assert len(evidence['attempts'])==1
    assert evidence['attempts'][0]['grid_role']=='requested_initial'
    assert evidence['effort']['outer_iterations']==0
