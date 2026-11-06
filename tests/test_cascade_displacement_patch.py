"""Boundary-condition and coupled-patch checks."""
import numpy as np
import pytest

from validation.cascade_displacement_patch import AttachedPatch, PatchFailure, solve_patches
from validation.periodic_cascade_reference import prepare
from validation.probe_periodic_cascade import geometry


def test_periodic_displacement_flux_against_cylinder_harmonic():
    angle = np.linspace(0., 2 * np.pi, 241)
    contour = np.c_[np.cos(angle), np.sin(angle)]
    contour[-1] = contour[0]
    system = prepare(contour, 1000., 12., 0., (0, len(contour) - 2))
    baseline = system.solve()
    empty = system.solve(np.zeros(len(contour)))
    np.testing.assert_allclose(empty.tangential_speed, baseline.tangential_speed, atol=1e-13)

    # Exterior potential -cos(angle)/r has normal speed cos(angle) and
    # tangential speed sin(angle) at r=1. Leave both Kutta panels inactive.
    flux = np.sin(angle)
    flux[[0, 1, -2, -1]] = 0.
    forced = system.solve(flux)
    mid = (angle[:-1] + angle[1:]) / 2
    away = abs(np.angle(np.exp(1j * mid))) > 0.35
    np.testing.assert_allclose(
        (forced.tangential_speed - baseline.tangential_speed)[away], np.sin(mid[away]), atol=0.015,
    )
    assert forced.net_source == pytest.approx(0., abs=1e-11)
    assert forced.circulation == pytest.approx(0., abs=1e-11)


def test_boundary_rejects_unclosed_flux_and_forcing_at_kutta_pair():
    xy, pitch, _, kutta, _ = geometry(48)
    system = prepare(xy, pitch, 33.28, 44.5, kutta)
    flux = np.zeros(len(xy))
    flux[-1] = 1.
    with pytest.raises(ValueError, match="periodic"):
        system.solve(flux)
    flux[-1] = 0.
    flux[kutta[0]] = 1.
    with pytest.raises(ValueError, match="Kutta"):
        system.solve(flux)


def test_two_prescribed_attached_intervals_exchange_pressure_through_one_core():
    angle = np.linspace(0., 2 * np.pi, 161)
    xy = np.c_[0.1 * np.cos(angle), 0.012 * np.sin(angle)]
    xy[-1] = xy[0]
    system = prepare(xy, 0.6, 33.28, 0., (0, 159))
    pressure, suction = np.arange(80, 161), np.arange(80, -1, -1)
    # Identical manufactured layers on a symmetric periodic ellipse.
    lower = AttachedPatch(pressure, .025, .046, 0.000035, 2.6)
    upper = AttachedPatch(suction, .025, .046, 0.000035, 2.6)
    options = dict(total_temperature=300., total_pressure=104000.)
    result = solve_patches(system, (lower, upper), **options)
    assert result.residual <= 1e-7 < result.initial_residual
    assert np.any(result.flux > 0) and np.any(result.flux < 0)
    assert np.diff(result.flux).sum() == pytest.approx(0., abs=1e-15)
    assert result.cascade.net_source == pytest.approx(0., abs=1e-11)
    assert result.cascade.circulation == pytest.approx(0., abs=1e-11)
    assert len(result.layers) == 2 and not any(layer.separated for layer in result.layers)
    np.testing.assert_allclose(result.layers[0].displacement_thickness,
                               result.layers[1].displacement_thickness, atol=1e-13)
    with pytest.raises(PatchFailure) as failed:
        solve_patches(system, (lower, upper), max_iterations=1, **options)
    assert failed.value.reason == "interaction_numerical_failure"
