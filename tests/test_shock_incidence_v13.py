"""Actual-flow turning in the NACA passage-shock model (RM E57A30 appendix B)."""
import numpy as np
import pytest

from sm_throughflow.correlations import aungier as A, blade_geometry as G
from sm_throughflow.solver.aungier_row import AungierCompressorRow, BladeSections
from sm_throughflow.solver.gas import PerfectGas
from sm_throughflow.solver.rows import ExitGeometry
from validation.phase3_rows import station


def inlet_and_model(beta, mach=1.3, rotor=False, cone=0.):
    gas = PerfectGas()
    r = np.linspace(.3, .4, 5)
    sign, omega = (-1., 900.) if rotor else (1., 0.)
    speed = mach*np.sqrt(gas.gamma*gas.R*250.)
    wm = np.full_like(r, speed*np.cos(np.radians(beta)))
    ct = omega*r + sign*speed*np.sin(np.radians(beta))
    t0 = 250.+(wm**2+ct**2)/(2*gas.cp)
    p0 = 50000.*(t0/250.)**(gas.gamma/(gas.gamma-1))
    inlet = station(r, np.zeros_like(r), wm, ct, t0, p0, omega, 5., gas)
    sec = BladeSections([0., 1.], [sign*50.]*2, [sign*30.]*2, [.05]*2, [.06]*2, coordinate='span')
    model = AungierCompressorRow(sec, 40, omega, profile='dca',
        expansion_angle=[10., 10.], shock_surface_angles=dict(leading=[60.,60.], foot=[50.,50.]))
    exit = ExitGeometry(inlet.t, inlet.y, r+.05*np.tan(np.radians(cone)), np.full_like(r,.05))
    return model._inlet_part(inlet, exit)


@pytest.mark.parametrize('rotor',[False,True])
def test_fixed_mach_shock_responds_to_actual_incidence_in_both_frames(rotor):
    low, tangent, high = [inlet_and_model(beta, rotor=rotor) for beta in (58.,60.,62.)]
    for beta,p in zip((58.,60.,62.), (low,tangent,high)):
        np.testing.assert_allclose(p['mach1'],1.3,atol=2e-15)
        np.testing.assert_allclose(p['shock_flow_turning'],beta-50.,atol=2e-13)
        np.testing.assert_allclose(p['suction_surface_incidence'],beta-60.,atol=2e-13)
        np.testing.assert_allclose(p['omega_shock'],A.shock_loss(1.3,beta-50.,PerfectGas().gamma),rtol=2e-13)
    assert np.all(low['omega_shock'] < tangent['omega_shock'])
    assert np.all(tangent['omega_shock'] < high['omega_shock'])
    # The historical surface-turning model is recovered at tangent incidence.
    np.testing.assert_allclose(tangent['omega_shock'],A.shock_loss(1.3,10.,PerfectGas().gamma))


def test_foot_tangent_and_flow_angle_use_same_meridional_frame():
    p=inlet_and_model(60.,cone=20.)
    projected=np.degrees(np.arctan(np.cos(np.radians(20.))*np.tan(np.radians(50.))))
    np.testing.assert_allclose(p['shock_flow_turning'],60.-projected,atol=2e-13)


def test_nonexpanding_supersonic_case_is_visible_and_subsonic_shock_stays_zero():
    p=inlet_and_model(48.)
    assert np.all(p['shock_compression_clipped'])
    np.testing.assert_allclose(p['omega_shock'],A.shock_loss(1.3,0.,PerfectGas().gamma))
    sub=inlet_and_model(48.,mach=.8)
    assert not np.any(sub['shock_compression_clipped'])
    np.testing.assert_array_equal(sub['omega_shock'],0.)


def test_constructed_foot_direction_agrees_with_independent_sharp_dca_circle():
    camber,stagger,tc,sigma=12.,54.,.05,1.4
    surface_turn=4*np.arctan(np.tan(np.radians(camber)/4)+tc)
    leading=np.radians(stagger)+surface_turn/2
    radius=.5/np.sin(surface_turn/2)
    centre=radius*np.array([np.sin(leading),-np.cos(leading)])
    radial=np.array([0.,1/sigma])-centre
    foot=np.degrees(np.arctan2(-radial[0],radial[1]))
    actual=G.suction_surface_shock_angles('dca','circular_arc',camber,stagger,tc,sigma,edge_radius=1e-6)
    assert actual[0]==pytest.approx(np.degrees(leading),abs=.04)
    assert actual[1]==pytest.approx(foot,abs=.04)


def test_malformed_shock_geometry_is_rejected():
    sec=BladeSections([.3,.4],[60.,60.],[40.,40.],[.05,.05],[.05,.05])
    for angles in (dict(leading=[60.],foot=[50.]),dict(leading=[60.,60.],foot=[50.,np.nan])):
        with pytest.raises(ValueError,match='matching finite span arrays'):
            AungierCompressorRow(sec,40,0.,shock_surface_angles=angles)
