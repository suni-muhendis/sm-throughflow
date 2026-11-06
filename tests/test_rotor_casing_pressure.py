import numpy as np
import pytest

from validation.audit_rotor_casing_pressure import decode_curve, difference, pressure_at


def test_digitized_axes_reverse_image_y_and_preserve_projected_chord():
    x, p, dx, dp = decode_curve([[0, 100], [50, 60], [100, 0]], [0, 100], [100, 0],
                               [-10, 110], [.7, 1.7], 2)
    np.testing.assert_allclose(x, [-.1, .5, 1.1])
    np.testing.assert_allclose(p, [.7, 1.1, 1.7])
    assert (dx, dp) == pytest.approx((.024, .02))


def test_pressure_band_includes_interior_knot_and_never_extrapolates():
    curve = np.array([0., .5, 1.]), np.array([1., 1.5, 1.]), .1, .02
    assert pressure_at(curve, .5) == pytest.approx((1.5, 1.38, 1.52))
    assert difference(pressure_at(curve, .2), pressure_at(curve, .5)) == pytest.approx((.3, .06, .44))
    with pytest.raises(ValueError, match="outside"):
        pressure_at(curve, .05)


def test_ambiguous_marker_order_is_rejected():
    with pytest.raises(ValueError, match="ordered"):
        decode_curve([[1, 30], [3, 20]], [0, 100], [100, 0], [0, 100], [.7, 1.7], 2)
