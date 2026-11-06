"""Independent geometric checks for the direct curvature discretization."""
import numpy as np
import pytest

from sm_throughflow.solver.geometry import _slope_and_curvature


@pytest.mark.parametrize('stretch', [1., 1.3])
def test_circle_curvature_including_endpoints_converges_at_second_order(stretch):
    errors = []
    for n in (21, 41, 81):
        angle = -.3+.6*np.linspace(0,1,n)**stretch
        radius = 1.7
        z, r = radius*np.sin(angle), 2.-radius*np.cos(angle)
        _, phi, kappa = _slope_and_curvature(z[:,None],r[:,None])
        errors.append(float(np.max(np.abs(radius*kappa+1.))))
        assert np.max(np.abs(phi[:,0]-angle)) < .002
    assert errors[1] < .001
    assert errors[0]/errors[1] > 3.5
    assert errors[1]/errors[2] > 3.5


def test_alternating_positions_are_not_a_zero_curvature_mode():
    # Two centered first derivatives miss this entire grid mode. The direct
    # second difference must see its 4*amplitude/dz**2 curvature magnitude.
    z = np.linspace(0,1,41)
    amplitude = 1e-5
    r = .3+amplitude*(-1.)**np.arange(z.size)
    _, _, kappa = _slope_and_curvature(z[:,None],r[:,None])
    expected = 4*amplitude/(z[1]-z[0])**2
    np.testing.assert_allclose(np.abs(kappa[2:-2,0]),expected,rtol=2e-10)
    assert np.all(kappa[2:-3,0]*kappa[3:-2,0]<0)


def test_parametric_geometry_is_rigid_motion_invariant():
    z = np.linspace(-.2,.3,23)**3
    r = .4+2*z*z
    m, phi, k = _slope_and_curvature(z[:,None],r[:,None])
    rotation = .23
    zz = np.cos(rotation)*z-np.sin(rotation)*r+.37
    rr = np.sin(rotation)*z+np.cos(rotation)*r-.11
    mm, pp, kk = _slope_and_curvature(zz[:,None],rr[:,None])
    np.testing.assert_allclose(mm,m,rtol=1e-10,atol=1e-15)
    np.testing.assert_allclose(pp,phi+rotation,rtol=1e-10,atol=1e-10)
    np.testing.assert_allclose(kk,k,rtol=1e-6,atol=1e-6)


@pytest.mark.parametrize('n', [1,2,7])
def test_straight_paths_have_zero_curvature_on_nonuniform_stations(n):
    z = np.linspace(0,1,n)**1.7
    r = .3+.2*z
    m, phi, kappa = _slope_and_curvature(z[:,None],r[:,None])
    np.testing.assert_allclose(m[:,0],np.sqrt(1.04)*z,atol=1e-14)
    np.testing.assert_allclose(kappa,0,atol=1e-13)
    if n>1:np.testing.assert_allclose(phi,np.arctan(.2),atol=1e-13)


def test_damping_four_contracts_resolved_high_frequency_mode_where_sixteen_grows():
    from sm_throughflow.solver.geometry import Annulus, QuasiNormals, uniform_flow_fractions
    from sm_throughflow.solver.throughflow import Throughflow, InletCondition
    from sm_throughflow.solver.gas import PerfectGas
    # Near-planar, low-Mach annulus: curvature couples the highest axial mode
    # to the first radial mode. For a direct second difference its asymptotic
    # relaxed gain is 1-4*B/pi**2, so B=16 is unstable and B=4 is contractive.
    gas = PerfectGas()
    h = gas.enthalpy(300.)
    entropy = gas.entropy(h,101325.)
    annulus = Annulus.from_points([(0.,10.),(.3,10.)],[(0.,10.1),(.3,10.1)])
    qn = QuasiNormals.on(annulus,np.linspace(0,.3,31))
    mass = np.pi*(10.1**2-10.**2)*gas.density(h-50.,entropy)*10.
    flow = Throughflow(annulus,qn,InletCondition(101325.,300.,alpha_deg=0.),mass,stream_surfaces=41)
    base = uniform_flow_fractions(qn,np.linspace(0,1,41))
    mode = np.sin(29*np.pi*np.arange(31)/30)[:,None]*np.sin(np.pi*base)
    mode[[0,-1]]=0.
    mode[:,[0,-1]]=0.
    positions = base+1e-6*mode
    result = flow._coupled_iteration(positions,[None]*31,{},1e-12)
    geo, stations, _, _, _, target, *_ = result
    gains = {}
    for damping in (4.,16.):
        updated = positions+flow._damping(geo,stations,damping)*(target-positions)
        gains[damping] = np.sum((updated-base)*mode)/np.sum((positions-base)*mode)
    assert abs(gains[4.]) < .7
    assert gains[16.] < -4.
