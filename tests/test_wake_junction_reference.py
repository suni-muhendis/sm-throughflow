import numpy as np
import pytest

from validation.wake_junction_reference import WakeMoments, join, march_momentum, pressure_deficits


def _moments(widths, q):
    return WakeMoments(
        widths @ (1 - q),
        widths @ (q * (1 - q)),
        widths @ (q * (1 - q**2)),
    )


def test_junction_preserves_all_defects_and_only_adds_displacement_for_stationary_gap():
    pressure_q, suction_q = np.array([.4, .9, 1.]), np.array([.2, .7, 1.])
    pressure_widths, suction_widths = np.array([1., 2., 3.]), np.array([2., 3., 4.])
    pressure = _moments(pressure_widths, pressure_q)
    suction = _moments(suction_widths, suction_q)
    gap = .6
    widths = np.r_[pressure_widths, gap, suction_widths]
    q = np.r_[pressure_q, 0., suction_q]
    wake = join(pressure, suction, dead_gap=gap)
    expected = _moments(widths, q)
    assert wake.displacement == pytest.approx(expected.displacement)
    assert wake.momentum == pytest.approx(expected.momentum)
    assert wake.kinetic_energy == pytest.approx(expected.kinetic_energy)
    assert wake == join(suction, pressure, dead_gap=gap)

    survey, mixed = pressure_deficits(wake, widths.sum())
    mixed_speed = widths @ q / widths.sum()
    mixed_static_rise = 2 * (widths @ (q * (q - mixed_speed))) / widths.sum()
    assert survey == pytest.approx(1 - (widths @ q**3) / (widths @ q))
    assert mixed == pytest.approx(1 - mixed_static_rise - mixed_speed**2)
    assert mixed > survey > 0


@pytest.mark.parametrize("speeds", [[10, 10, 10, 10], [10, 15, 20, 25], [25, 20, 15, 10]])
def test_constant_shape_has_exact_power_law_for_any_monotonic_edge(speeds):
    shape = 1.6
    speed = np.array(speeds)
    theta = march_momentum([0, .1, .4, 1], speed, [shape] * 4, .002)
    np.testing.assert_allclose(theta, .002 * (speed / speed[0])**(-2 - shape), rtol=1e-12)


def test_impossible_finite_width_moments_and_duplicate_stations_raise():
    with pytest.raises(ValueError, match="cannot represent"):
        pressure_deficits(WakeMoments(1, .9, 1.6), 1.5)
    with pytest.raises(ValueError, match="ordered wake stations"):
        march_momentum([0, 0], [1, 1], [1.5, 1.5], .002)
    with pytest.raises(ValueError, match="nonnegative dead gap"):
        join(WakeMoments(1, .5, .7), WakeMoments(1, .5, .7), dead_gap=-1)
