"""Aungier's (2003) compressor cascade correlations, pinned to the book's figures.

tests/fixtures/aungier_2003_figures.json holds the circle markers of figures
6-2 to 6-18, digitized from the book's pages. In every figure but 6-3 the
circles are Aungier's equation, so they check the transcription; in 6-3 they
are Johnsen and Bullock's data, so they check the fit.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from sm_throughflow.correlations import aungier as A

FIGURES = json.loads((Path(__file__).parent / "fixtures" / "aungier_2003_figures.json").read_text())


def _loss_D(D):
    return 0.0035 * (1 + 3.5 * D + 37 * D ** 4)  # omega* cos(beta2*)/(2 sigma), (6-34)


def _loss_Deq(Deq):
    return 0.004 * (1 + 3.1 * (Deq - 1) ** 2 + 0.4 * (Deq - 1) ** 8)  # (6-37)


def _curve(figure, name):
    key = name.split("=")[-1]
    if figure == "6-2":
        return lambda s: A.design_angle_of_attack(A.camber_from_lift_coefficient(float(key)), s)
    if figure == "6-3":
        return A.thickness_incidence_factor
    if figure == "6-4":
        return lambda b: A.lieblein_zero_camber_incidence(b, float(key))
    if figure == "6-5":
        return lambda b: A.lieblein_incidence_slope(b, float(key))
    if figure == "6-6":
        return lambda b: A.lieblein_zero_camber_deviation(b, float(key))
    if figure == "6-7":
        return lambda b: A.lieblein_deviation_slope(b, 1.0, name)
    if figure == "6-8":
        return lambda b: 0.9625 - 0.17 * b / 100 - 0.85 * (b / 100) ** 3  # (6-24), inside (6-21)
    if figure == "6-9":
        return A.thickness_deviation_factor
    if figure == "6-11":
        return _loss_D
    if figure == "6-12":
        return _loss_Deq
    if figure == "6-14":
        if name.startswith("pos"):
            return lambda th: A.stall_angles_of_attack(0.0, th, 30.0, float(key))[1]
        return lambda th: A.stall_angles_of_attack(0.0, th, float(key), 45.0)[0]
    if figure == "6-18":
        return lambda s: A.deviation_slope(float(key), s)
    raise KeyError(figure)


# (median, maximum) tolerance on |equation - figure|, in the figure's units.
# Maxima come from circles that touch a line end, a label or each other.
TOLERANCE = {
    "6-2": (0.05, 0.3),
    "6-3": (0.03, 0.08),
    "6-4": (0.03, 0.12),
    "6-5": (0.001, 0.006),
    "6-6": (0.02, 0.02),
    "6-7": (0.0005, 0.001),
    "6-8": (0.001, 0.0015),
    "6-9": (0.008, 0.01),
    "6-11": (0.0001, 0.0002),
    "6-12": (0.0002, 0.0004),
    "6-14": (0.03, 0.65),
    "6-18": (0.003, 0.04),
}


@pytest.mark.parametrize("figure", sorted(TOLERANCE))
def test_equations_reproduce_the_figure(figure):
    points = FIGURES[figure]
    assert len(points) >= 7
    diffs = np.array([abs(float(_curve(figure, name)(x)) - y) for x, y, name in points])
    median, maximum = TOLERANCE[figure]
    assert np.median(diffs) <= median
    assert np.max(diffs) <= maximum


def test_lift_coefficient_and_camber_are_inverse():
    cl = np.array([0.0, 0.4, 1.2, 2.7])
    assert A.lift_coefficient_from_camber(A.camber_from_lift_coefficient(cl)) == pytest.approx(cl)
    # (4-28) vs (4-29): 33.8 and 33.5 deg at C_l0 = 1 for the A4K6 camberline, a/c = 0.375.
    assert A.camber_from_lift_coefficient(1.0, 0.375) == pytest.approx(33.5, abs=0.05)
    # NACA-65, a/c = 0.5: tan(theta/4) = 0.1103 C_l0 (4-6).
    assert np.tan(np.radians(A.camber_from_lift_coefficient(1.0)) / 4) == pytest.approx(0.1103)


def test_lieblein_incidence_for_a_blade_satisfies_its_own_inlet_angle():
    kappa1, camber, sigma = 45.0, 30.0, 1.2
    i_star = A.lieblein_design_incidence_for_blade(kappa1, camber, sigma)
    assert i_star == pytest.approx(A.lieblein_design_incidence(kappa1 + i_star, camber, sigma), abs=1e-10)


def test_stall_angles_for_a_blade_satisfy_their_own_inlet_angles():
    alpha_star, camber, stagger = 8.0, 30.0, 35.0
    alpha_c, alpha_s = A.stall_angles_for_blade(alpha_star, camber, stagger)
    again_c, again_s = A.stall_angles_of_attack(alpha_star, camber, alpha_c + stagger, alpha_s + stagger)
    assert (alpha_c, alpha_s) == pytest.approx((float(again_c), float(again_s)), abs=1e-10)


def test_klapproth_annular_form_reduces_to_the_two_dimensional_one():
    beta1, beta2, sigma, cm = 50.0, 25.0, 1.3, 150.0
    c_theta1, c_theta2 = cm * np.tan(np.radians(beta1)), cm * np.tan(np.radians(beta2))
    annular = A.max_velocity_ratio_annular(beta1, sigma, 0.3, c_theta1, 0.3, c_theta2, cm)
    assert annular == pytest.approx(A.max_velocity_ratio(beta1, beta2, sigma))


def test_off_design_loss_is_continuous_at_its_joins():
    i_m, i_c, i_s, omega_m = 2.0, -6.0, 9.0, 0.03
    for xi in (-2.0, 1.0):
        i = i_m + xi * ((i_s - i_m) if xi > 0 else (i_m - i_c))
        below, above = A.off_design_loss([i - 1e-9, i + 1e-9], i_m, i_c, i_s, omega_m)
        assert below == pytest.approx(above, rel=1e-6)
    # The loss doubles at the stall incidences (Fig. 6-13) and is minimum at i_m.
    assert A.off_design_loss([i_c, i_m, i_s], i_m, i_c, i_s, omega_m) == pytest.approx([2 * omega_m, omega_m, 2 * omega_m])


def test_mach_number_narrows_the_low_loss_range():
    i_c, i_s = A.stall_incidence(2.0, 8.0, 9.0, [0.0, 0.8])
    assert i_c[0] == pytest.approx(-6.0) and i_s[0] == pytest.approx(11.0)
    assert i_c[1] > -6.0 and i_s[1] < 11.0
    # The minimum-loss incidence lies at the same fraction of the range (6-55).
    assert A.minimum_loss_incidence(-6.0, 11.0, 8.0, 9.0) == pytest.approx(2.0)


def test_wake_blockage_starts_at_the_diffusion_limit():
    assert A.wake_blockage([1.5, 2.0, 2.5]) == pytest.approx([0.0, 0.0, 1 - 0.8 ** 0.9])


def test_reynolds_factor_vanishes_at_the_reference_reynolds_number():
    assert A.reynolds_loss_factor([2.5e5]) == pytest.approx([0.0], abs=1e-12)
    laminar, turbulent = A.reynolds_loss_factor([1e5, 1e6])
    assert laminar > 0 > turbulent


def test_deviation_moves_with_incidence_and_axial_velocity_ratio():
    slope = A.deviation_slope(40.0, 1.0)
    assert A.off_design_deviation(5.0, slope, 4.0, 2.0) == pytest.approx(5.0 + 2.0 * slope)
    assert A.off_design_deviation(5.0, slope, 4.0, 2.0, wm_ratio=0.9) == pytest.approx(5.0 + 2.0 * slope + 1.0)
    assert A.off_design_deviation(5.0, slope, 4.0, 2.0, inlet_guide_vane=True) == pytest.approx(5.0)
