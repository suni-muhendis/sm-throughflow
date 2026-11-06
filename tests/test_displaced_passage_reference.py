"""Similarity and conservation checks for the stagnation and feedback steps."""
import numpy as np
import pytest
from scipy.integrate import quad, solve_bvp

from sm_throughflow.solver.endwall import sutherland_air
from validation.blade_layer_reference import march_from_stagnation, stagnation_seed
from validation.displaced_passage_reference import PassageFailure, _inlet_capacity, solve


def test_stagnation_seed_against_hiemenz_similarity_solution():
    eta = np.linspace(0., 10., 100)
    decay = np.exp(-eta)

    def similarity(_eta, state):
        f, speed, shear = state
        return np.array([speed, shear, speed**2 - 1 - f * shear])

    exact = solve_bvp(similarity, lambda a, b: [a[0], a[1], b[1] - 1], eta,
                      np.array([eta - 1 + decay, 1 - decay, decay]), tol=1e-10, max_nodes=10000)
    assert exact.success
    displacement = quad(lambda x: 1 - exact.sol(x)[1], 0, eta[-1])[0]
    momentum = quad(lambda x: exact.sol(x)[1] * (1 - exact.sol(x)[1]), 0, eta[-1])[0]
    slope, temperature, pressure = 2500., 300., 100000.
    nu = float(sutherland_air(temperature) * 287.05 * temperature / pressure)
    theta, hk = stagnation_seed(slope, temperature, pressure)
    assert theta / np.sqrt(nu / slope) == pytest.approx(momentum, rel=0.025)
    assert hk == pytest.approx(displacement / momentum, rel=0.025)

    # A linear low-speed edge retains the stagnation similarity thickness.
    arc = np.linspace(0., 0.004, 20)
    result = march_from_stagnation(arc, slope * arc, total_temperature=temperature,
                                   total_pressure=pressure)
    assert not result.separated
    np.testing.assert_allclose(result.momentum_thickness, theta, rtol=0.002)
    np.testing.assert_allclose(result.kinematic_shape, hk, rtol=0.002)


def test_pressure_feedback_balances_mass_and_changes_the_pressure():
    arc = np.linspace(0, 0.06, 17)
    gap = np.full_like(arc, 0.012)
    mass, tt, pt = 1.1, 300., 100000.
    options = dict(mass_per_span=mass, total_temperature=tt, total_pressure=pt,
                   theta0=0.00009, hk0=2.59)
    result = solve(arc, gap, **options)
    repeat = solve(arc, gap, **options)
    assert np.array_equal(result.static_pressure, repeat.static_pressure)
    assert result.iterations == repeat.iterations
    assert result.relative_mass_residual < 1e-8
    assert result.relative_gap_residual < 1e-8
    assert np.all(result.effective_gap < gap)
    assert result.static_pressure[-1] < result.static_pressure[0]
    temperature = tt - result.velocity**2 / (2 * 1004.675)
    flux = result.static_pressure / (287.05 * temperature) * result.velocity * result.effective_gap
    np.testing.assert_allclose(flux, mass, rtol=1e-8)


def test_inlet_capacity_matches_independent_mach_sweep():
    mach = np.linspace(0, 1, 100001)
    temp = 300. / (1 + 0.2 * mach**2)
    pressure = 100000. * (temp / 300.)**3.5
    velocity = mach * np.sqrt(1.4 * 287.05 * temp)
    thickness = 0.00009 * (2.59 * (1 + 0.113 * mach**2) + 0.29 * mach**2)
    mass = pressure / (287.05 * temp) * velocity * (0.012 - 2 * thickness)
    expected = mass.max()
    assert 0.98 < mach[mass.argmax()] < 1
    assert _inlet_capacity(0.012, 0.00009, 2.59, 300., 100000.) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize(("mass", "theta0", "budget", "reason"), [
    (3., 0.00009, 80, "geometric_capacity"),
    (2.75, 0.0002, 80, "prescribed_inlet_capacity"),
    (2.66, 0.00009, 80, "unresolved_displacement_capacity"),
    (1.1, 0.00009, 1, "interaction_numerical_failure"),
])
def test_capacity_and_iteration_failures_are_distinct(mass, theta0, budget, reason):
    arc = np.linspace(0, 0.06, 9)
    with pytest.raises(PassageFailure) as raised:
        solve(arc, np.full_like(arc, 0.012), mass_per_span=mass,
              total_temperature=300., total_pressure=100000., theta0=theta0,
              hk0=2.59, max_iterations=budget)
    assert raised.value.reason == reason
