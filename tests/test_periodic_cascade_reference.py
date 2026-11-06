"""Potential-flow limits and control-volume checks for the cascade."""
import numpy as np
import pytest

from validation.periodic_cascade_reference import solve
from validation.probe_periodic_cascade import evaluate


def test_large_pitch_recovers_isolated_circular_cylinder_pressure():
    angle = np.linspace(0., 2 * np.pi, 161)
    xy = np.c_[np.cos(angle), np.sin(angle)]
    xy[-1] = xy[0]
    result = solve(xy, 1000., 12., 0., (0, len(xy) - 2))
    angle_c = np.arctan2(result.centres[:, 1], result.centres[:, 0])
    np.testing.assert_allclose(result.pressure_coefficient, 1 - 4 * np.sin(angle_c)**2, atol=0.075)
    assert result.circulation == pytest.approx(0., abs=1e-11)
    assert result.net_source == pytest.approx(0., abs=1e-11)


def test_dca_force_matches_far_field_momentum_under_refinement():
    coarse = evaluate(48, run_layers=False)
    fine = evaluate(768, run_layers=False)
    assert fine["relative_force_residual"] < 0.003
    assert fine["relative_force_residual"] < coarse["relative_force_residual"]
    assert fine["normal_residual"] < coarse["normal_residual"]
    assert fine["net_source"] == pytest.approx(0., abs=1e-11)
