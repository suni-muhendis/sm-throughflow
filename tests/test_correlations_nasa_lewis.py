"""The NASA Lewis design code's deviation rule (correlations.nasa_lewis)."""
import numpy as np
import pytest

from sm_throughflow.correlations import nasa_lewis as L


def test_carter_coefficient_at_mid_chord_camber_is_the_fitted_x():
    """At a/c = 0.5 the exponent drops out: m = x(gamma) (TN D-7345 eq. 21)."""
    for gamma in (0.0, 30.0, 60.0):
        x = 0.219 + 0.0008916 * gamma + 0.000027085 * gamma ** 2
        assert float(L.carter_deviation_coefficient(gamma, 0.5)) == pytest.approx(x, rel=1e-12)


def test_carter_coefficient_agrees_with_the_ge_curves_at_high_stagger():
    """GE CR-54581 fig. 9 and the Lewis fit agree at gamma = 60 deg, a/c = 0.8 (about 0.52)."""
    assert float(L.carter_deviation_coefficient(60.0, 0.8)) == pytest.approx(0.52, abs=0.02)


def test_carter_deviation_scales_with_camber_and_solidity():
    d1 = L.carter_deviation(10.0, 50.0, 0.55, 1.0)
    assert float(L.carter_deviation(20.0, 50.0, 0.55, 1.0)) == pytest.approx(2.0 * d1)
    assert float(L.carter_deviation(10.0, 50.0, 0.55, 4.0)) == pytest.approx(0.5 * d1)
    assert float(L.carter_deviation(10.0, -50.0, 0.55, 1.0)) == pytest.approx(d1)  # the setting angle enters by magnitude
    assert np.shape(L.carter_deviation(np.ones(3), 50.0, 0.55, 1.2)) == (3,)
