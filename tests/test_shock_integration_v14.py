"""Independent sonic-cut integrals and continuous geometric shock-foot tests."""
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

from sm_throughflow.correlations import aungier as A, blade_geometry as G
from sm_throughflow.solver import shock_integration as SI


def weights(x):
    return np.diff(np.r_[0., .5*(x[:-1]+x[1:]), 1.])


@pytest.mark.parametrize('offset',[-1e-8,0.,1e-8,.07])
def test_sonic_step_integral_is_exact_on_nonuniform_mass_cells(monkeypatch,offset):
    # A manufactured discontinuity has a closed-form integral, independent
    # of the implementation's quadrature or surface positions.
    x=np.array([0.,.1,.4,.65,1.]);m=.6+x+offset;head=2.+3.*x
    monkeypatch.setattr(SI,'shock_loss',lambda m,*args:np.where(m>1.,2.,0.))
    loss=SI.integrated_shock_loss(m,np.full_like(x,10.),head,np.diff(x))
    edges=np.r_[0.,.5*(x[:-1]+x[1:]),1.]
    a=np.maximum(edges[:-1],.4-offset);b=edges[1:]
    exact=np.where(b>a,4*(b-a)+3*(b*b-a*a),0.)
    np.testing.assert_allclose(loss*head*np.diff(edges),exact,atol=3e-15)
    np.testing.assert_array_equal(loss,SI.integrated_shock_loss(m,np.full_like(x,10.),head,np.diff(x)))


def test_physical_shock_pressure_integral_agrees_with_adaptive_quadrature():
    x=np.array([0.,.12,.31,.52,.7,1.]);m=.83+.45*x;turn=8.+9.*x;head=30000.+45000.*x
    result=SI.integrated_shock_loss(m,turn,head,np.diff(x))
    sonic=(1.-.83)/.45
    oracle=quad(lambda q:float(A.shock_loss(.83+.45*q,8.+9.*q))*(30000.+45000.*q),sonic,1.,epsabs=1e-8)[0]
    assert np.dot(result*head,weights(x))==pytest.approx(oracle,rel=2e-6)
    reverse=SI.integrated_shock_loss(m[::-1],turn[::-1],head[::-1],np.diff(x)[::-1])
    np.testing.assert_allclose(reverse[::-1],result,atol=1e-14)


def test_sonic_contour_crossing_a_node_does_not_switch_a_whole_cell():
    x=np.linspace(0.,1.,11);head=np.ones_like(x);turn=np.full_like(x,18.)
    def evaluate(delta):return SI.integrated_shock_loss(.8+.4*x+delta,turn,head,np.diff(x))
    large=np.max(abs(evaluate(1e-5)-evaluate(-1e-5)))
    small=np.max(abs(evaluate(1e-7)-evaluate(-1e-7)))
    assert small<large/80
    assert small<1e-6
    assert A.shock_loss(1.+1e-7,18.)-A.shock_loss(1.-1e-7,18.)>.05


def test_uniform_supersonic_limit_and_entirely_subsonic_limit():
    x=np.linspace(0.,1.,9);head=np.full_like(x,40000.)
    for mach in (.9,1.,1.4):
        result=SI.integrated_shock_loss(np.full_like(x,mach),np.full_like(x,10.),head,np.diff(x))
        np.testing.assert_allclose(result,A.shock_loss(mach,10.),atol=1e-15)


def test_span_refinement_converges_to_independent_nonlinear_profile_integral():
    def m(x):return .8+.5*x*x
    def turn(x):return 10.+5.*x*x
    def head(x):return 1.+x*x
    sonic=np.sqrt(.4)
    reference=quad(lambda x:float(A.shock_loss(m(x),turn(x)))*head(x),sonic,1.,epsabs=1e-10)[0]
    errors=[]
    for n in (17,33,65):
        x=np.linspace(0,1,n)**1.2
        losses=SI.integrated_shock_loss(m(x),turn(x),head(x),np.diff(x))
        errors.append(abs(np.dot(losses*head(x),weights(x))-reference))
    assert errors[0]/errors[1]>3.5 and errors[1]/errors[2]>3.5


@pytest.mark.parametrize('bad',['mass','head','shape','nan'])
def test_invalid_shock_integration_inputs_rejected(bad):
    m=np.array([.9,1.1,1.3]);turn=np.ones(3);head=np.ones(3);mass=np.ones(2)
    if bad=='mass':mass[0]=0
    if bad=='head':head[0]=-1
    if bad=='shape':turn=turn[:2]
    if bad=='nan':m[0]=np.nan
    with pytest.raises(ValueError,match='finite span fields'):SI.integrated_shock_loss(m,turn,head,mass)


def test_projected_circle_foot_matches_independent_ellipse_minimum():
    # The cylindrical circle becomes an ellipse on a sloping meridional
    # plane. Finding a cylindrical foot and merely rotating its tangent is
    # not the same calculation.
    angle=np.linspace(np.radians(68.),np.radians(36.),1001)
    radius=2.;centre=radius*np.array([np.sin(angle[0]),-np.cos(angle[0])])
    p=centre+radius*np.column_stack([-np.sin(angle),np.cos(angle)])
    cp=np.cos(np.radians(35.))
    def distance(a):
        v=centre+radius*np.array([-np.sin(a),np.cos(a)])
        return (v[0]/cp)**2+(v[1]-1.)**2
    exact=minimize_scalar(distance,bounds=(angle[-1],angle[0]),method='bounded',options={'xatol':1e-14}).x
    _,foot=G.projected_surface_shock_angles(p[None,:,:],np.array([cp]))
    assert foot[0]==pytest.approx(np.degrees(np.arctan(cp*np.tan(exact))),abs=2e-5)
    _,flat=G.projected_surface_shock_angles(p[None,:,:],np.ones(1))
    assert abs(foot[0]-np.degrees(np.arctan(cp*np.tan(np.radians(flat[0])))))>.1


def test_tiny_solidity_changes_move_the_foot_continuously():
    def foot(sigma):return G.suction_surface_shock_angles('dca','circular_arc',12.,54.,.05,sigma,edge_radius=.001)[1]
    a,b,c=[foot(1.4+d) for d in (-1e-5,0.,1e-5)]
    assert 1e-7<abs(b-a)<.001
    assert c-b==pytest.approx(b-a,rel=1e-4)


def test_stage53_regression_converges_repeatedly_with_unchanged_balances():
    from sm_throughflow.contracts import SIMULATOR_VERSION,ThroughflowDesignV2,ThroughflowTaskV2
    from sm_throughflow.simulator import SlcAungierSimulator
    job=json.loads((Path(__file__).parent/'fixtures/v13_stage53_2993_job.json').read_text())
    job['task']['simulator_version']=SIMULATOR_VERSION
    design=ThroughflowDesignV2.model_validate(job['design']);task=ThroughflowTaskV2.model_validate(job['task'])
    first=None
    for _ in range(2):
        flow,_,sol,balances,_=SlcAungierSimulator.solve_state(design,task,task.operating_points[0])
        assert sol.convergence.converged
        assert max(sol.convergence.position_change[-1],sol.convergence.velocity_change[-1])<=1e-7
        assert balances['mass_relative_error']<1e-9
        assert balances['energy_relative_error']<1e-10
        if first is not None:
            assert first.convergence==sol.convergence
            for a,b in zip(first.stations,sol.stations):np.testing.assert_array_equal(a.P0,b.P0)
        first=sol
