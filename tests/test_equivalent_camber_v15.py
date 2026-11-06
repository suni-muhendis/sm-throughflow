"""NASA design-mode forward equations are an independent inverse-row oracle."""
import numpy as np
import pytest

from sm_throughflow.correlations import nasa_lewis as L
from sm_throughflow.correlations import aungier as A
from sm_throughflow.solver.aungier_row import AungierCompressorRow, BladeSections
from sm_throughflow.solver.gas import PerfectGas
from sm_throughflow.solver.rows import ExitGeometry
from validation.phase3_rows import station


@pytest.mark.parametrize('signed_omega', [-900., 0., 900.])
def test_inverse_recovers_forward_nasa_blade_design(signed_omega):
    # Follow BLADE in design mode: prescribed flow -> equivalent exit flow
    # -> equivalent camber -> metal exit angle. Then invert the known blade.
    r1 = np.array([.28, .34, .41])
    r2 = r1*np.array([.96, 1., 1.04])
    v1 = np.array([130., 160., 180.]); v2 = v1*np.array([.85, 1., 1.15])
    beta1 = np.array([55., 60., 65.]); beta2 = np.array([32., 40., 45.])
    incidence = np.array([1., 2., -1.])
    gamma, ac, sigma = 45., .58, 1.4
    q = L.carter_deviation_coefficient(gamma, ac)/np.sqrt(sigma)
    # Compute absolute circulation explicitly, not using the inverse's a,b.
    ctheta2 = v2*np.tan(np.radians(beta2))+signed_omega*r2
    transported = r2*ctheta2/r1-signed_omega*r1
    b2eq = np.degrees(np.arctan2(transported, v1))
    equivalent_camber = (beta1-b2eq-incidence)/(1-q)
    expected = q*equivalent_camber
    k1, k2 = beta1-incidence, beta2-expected
    actual = L.annular_carter_deviation(k1, k2, gamma, ac, sigma, v1, v2, r1, r2, signed_omega)
    np.testing.assert_allclose(actual, expected, atol=6e-14, rtol=0.)


def test_equal_velocity_cylinder_recovers_cascade_carter_exactly():
    k1, k2 = np.array([20., 50., 70.]), np.array([-10., 30., 50.])
    for omega in (-1000., 0., 1000.):
        actual = L.annular_carter_deviation(k1, k2, 40., .55, 1.6, 150., 150., .3, .3, omega)
        np.testing.assert_allclose(actual, L.carter_deviation(k1-k2, 40., .55, 1.6), atol=4e-14)


def test_similarity_units_and_repeat_are_invariant():
    args = (60., 40., 50., .55, 1.3)
    first = L.annular_carter_deviation(*args, 150., 130., .3, .32, -700.)
    same = L.annular_carter_deviation(*args, 450., 390., 2.1, 2.24, -300.)
    assert same == pytest.approx(first, abs=5e-14)
    assert first == L.annular_carter_deviation(*args, 150., 130., .3, .32, -700.)


def test_velocity_change_is_geometry_dependent_and_not_a_fixed_ten_degree_slope():
    low = L.annular_carter_deviation(50., 25., 40., .5, 1.5, 150., 120., .3, .3)
    high = L.annular_carter_deviation(50., 25., 40., .5, 1.5, 150., 180., .3, .3)
    nominal = L.carter_deviation(25., 40., .5, 1.5)
    assert low > nominal > high
    assert abs(low-nominal-2.) > .5


@pytest.mark.parametrize('field,value', [('wm1', 0.), ('wm2', -1.), ('r1', 0.), ('r2', -1.),
    ('solidity', .001), ('a_c', 0.), ('kappa1', 90.), ('kappa2', -90.), ('stagger', 90.), ('signed_omega', np.nan)])
def test_invalid_or_nonunique_correlation_domain_is_rejected(field, value):
    args = dict(kappa1=60., kappa2=40., stagger=50., a_c=.5, solidity=1.3,
                wm1=150., wm2=130., r1=.3, r2=.32, signed_omega=-700.)
    args[field] = value
    with pytest.raises(ValueError, match='annular Carter'):
        L.annular_carter_deviation(**args)


@pytest.mark.parametrize('rotor', [False, True])
def test_row_recomputes_exit_dependent_reference_and_does_not_double_count_velocity(rotor):
    gas = PerfectGas(); r = np.linspace(.3, .4, 5)
    sign, omega = (-1., 500.) if rotor else (1., 0.)
    wm = np.full_like(r, 100.); ct = sign*wm*np.tan(np.radians(58.))+omega*r
    total_t, total_p = np.full_like(r, 330.), np.full_like(r, 150000.)
    inlet = station(r, 0.*r, wm, ct, total_t, total_p, omega, 5., gas)
    geometry = ExitGeometry(inlet.t, inlet.y, r*1.02, .05+0.*r)
    sec = BladeSections([0., 1.], [sign*55.]*2, [sign*35.]*2, [.06]*2, [.05]*2, coordinate='span')
    model = AungierCompressorRow(sec, 45, omega, profile='mca', smoothing=False,
        section_shape=dict(a_c=[.5, .5], chi1_over_camber=[.5, .5]))
    outputs = []
    for ratio in (.8, 1.2, .8):
        exit = station(geometry.r, geometry.z, wm*ratio, ct, total_t, total_p, omega, 5., gas)
        result = model(inlet, exit, geometry); d = result.diagnostics
        assert d['equivalent_carter_active']
        g = model._cached[2]['g']; q = L.carter_deviation_coefficient(g['stagger'], g['a_c'])/np.sqrt(g['sigma'])
        beta2 = g['k2']+d['design_deviation']
        absolute_swirl = sign*exit.Wm*np.tan(np.radians(beta2))+omega*geometry.r
        equivalent = sign*np.degrees(np.arctan2(geometry.r*absolute_swirl/r-omega*r, wm))
        np.testing.assert_allclose(d['design_deviation'], q*(g['k1']-equivalent)/(1-q), atol=5e-13)
        np.testing.assert_allclose(d['deviation']-d['design_deviation'],
            A.deviation_slope(abs(g['k1']+d['design_incidence']), g['sigma'])*
            (d['incidence']-d['design_incidence']), atol=5e-13)
        # The same reference exit angle also drives the reference loss triangle.
        beta1 = g['k1']+d['design_incidence']
        c1 = wm*np.tan(np.radians(beta1))+sign*omega*r
        maximum = A.max_velocity_ratio_annular(beta1, g['sigma'], r, c1,
                                              geometry.r, sign*absolute_swirl, wm)
        expected_diffusion = maximum*np.cos(np.radians(beta2))/(ratio*np.cos(np.radians(beta1)))
        np.testing.assert_allclose(d['design_equivalent_diffusion'], expected_diffusion, atol=5e-14)
        outputs.append(result)
    assert np.max(abs(outputs[0].exit_angle-outputs[1].exit_angle)) > .01
    np.testing.assert_array_equal(outputs[0].loss, outputs[2].loss)
    np.testing.assert_array_equal(outputs[0].exit_angle, outputs[2].exit_angle)
