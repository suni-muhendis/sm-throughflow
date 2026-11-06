"""Independent limits for the direct laminar layer march."""
import numpy as np
import pytest

from sm_throughflow.solver.endwall import sutherland_air
from validation.blade_layer_reference import march


def test_zero_gradient_blasius_limit_and_kinetic_energy_balance():
    u = 10.
    arc = np.array([0.05, 0.20, 0.40])
    t0, p0 = 300., 100000.
    cp = 1.4 * 287.05 / 0.4
    t = t0 - u**2 / (2 * cp)
    rho = p0 * (t / t0)**3.5 / (287.05 * t)
    nu = float(sutherland_air(t) / rho)
    theta = 0.664114 * np.sqrt(nu * arc / u)
    result = march(arc, np.full_like(arc, u), theta0=theta[0], hk0=2.5911,
                   total_temperature=t0, total_pressure=p0, rtol=1e-10)
    assert not result.separated
    np.testing.assert_allclose(result.momentum_thickness, theta, rtol=0.025)
    assert result.kinematic_shape[-1] == pytest.approx(2.5911, rel=0.025)
    assert result.skin_friction[-1] == pytest.approx(0.664114 / np.sqrt(u * arc[-1] / nu), rel=0.025)
    energy_thickness = result.kinetic_shape * result.momentum_thickness
    np.testing.assert_allclose(
        result.dissipation_power_per_span, 0.5 * rho * u**3 * (energy_thickness - energy_thickness[0]),
        rtol=2e-8,
    )


def test_adverse_gradient_terminates_at_zero_shear_and_keeps_sampling_independent():
    arc = np.linspace(0., 0.08, 12)
    velocity = 47. - 300. * arc
    initial = dict(theta0=0.00015, hk0=2.65, total_temperature=300., total_pressure=100000.)
    coarse = march(arc, velocity, **initial)
    dense = march(arc, velocity, sample_at=np.linspace(0., 0.08, 37), **initial)
    assert coarse.separated and dense.separated
    assert 0 < coarse.arc[-1] < arc[-1]
    assert coarse.arc[-1] == dense.arc[-1]
    assert coarse.skin_friction[-1] == pytest.approx(0., abs=1e-12)
    assert np.all(coarse.skin_friction[:-1] > 0)
    assert np.all(np.diff(coarse.dissipation_power_per_span) > 0)


def test_smooth_transonic_acceleration_keeps_positive_defects():
    # An isentropic manufactured edge crosses Mach one smoothly.
    arc = np.linspace(0., 0.05, 9)
    speed = np.linspace(290., 350., arc.size)
    state = march(arc, speed, theta0=0.00008, hk0=2.55,
                  total_temperature=300., total_pressure=100000.)
    assert not state.separated
    assert np.all(state.displacement_thickness > state.momentum_thickness)
    assert np.all(state.skin_friction > 0)
    assert np.all(np.diff(state.dissipation_power_per_span) > 0)


def test_rejects_separated_seed_and_nonphysical_edge():
    with pytest.raises(ValueError, match="attached"):
        march([0, 1], [15, 15], theta0=0.001, hk0=4.3,
              total_temperature=300., total_pressure=100000.)
    with pytest.raises(ValueError, match="static temperature"):
        march([0, 1], [15, 1000], theta0=0.001, hk0=2.6,
              total_temperature=300., total_pressure=100000.)
