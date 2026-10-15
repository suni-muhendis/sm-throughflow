"""Blade sections and cascade throats (Aungier, 2003, chapter 4)."""
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial import cKDTree

from sm_throughflow.correlations import blade_geometry as G
from sm_throughflow.correlations.aungier import (camber_from_lift_coefficient, camberline_angles, lift_coefficient_from_camber, suction_surface_expansion_angle,
                                                 throat_opening_ratio)

THROAT_LINES = json.loads((Path(__file__).parent / "fixtures" / "aungier_2003_throat_lines.json").read_text())


def test_thickness_tables():
    # Table 4-1, with the 2.5% station of the NACA 65-010 corrected to Report 824's 2 x 1.574.
    assert G.NACA65_010_THICKNESS[list(G.NACA65_STATIONS).index(2.5)] == pytest.approx(3.148)
    assert G.NACA65_STATIONS[np.argmax(G.NACA65_010_THICKNESS)] == 40.0  # maximum thickness at 40% chord
    assert G.C4_STATIONS[np.argmax(G.C4_THICKNESS)] == 30.0 and G.C4_THICKNESS.max() == 10.0
    assert np.all(np.diff(G.NACA65_010_THICKNESS[:14]) > 0) and np.all(np.diff(G.NACA65_010_THICKNESS[13:]) < 0)


@pytest.mark.parametrize("camber", [10.0, 30.0, 50.0])
def test_circular_and_parabolic_camberlines(camber):
    x, y = G.camberline("circular_arc", camber, points=4001)
    assert y.max() == pytest.approx(0.5 * np.tan(np.radians(camber) / 4), rel=1e-6)  # (4-10)
    slope = np.degrees(np.arctan2(y[1] - y[0], x[1] - x[0]))
    assert slope == pytest.approx(camber / 2, abs=0.05)  # (4-35)
    for a_c in (0.35, 0.5, 0.65):
        x, y = G.camberline("parabolic_arc", camber, a_c, points=4001)
        chi1, chi2 = camberline_angles(camber, a_c)
        assert np.degrees(np.arctan2(y[1] - y[0], x[1] - x[0])) == pytest.approx(float(chi1), abs=0.05)  # (4-17)
        assert np.degrees(np.arctan2(y[-2] - y[-1], x[-1] - x[-2])) == pytest.approx(float(chi2), abs=0.05)  # (4-18)
        assert x[np.argmax(y)] == pytest.approx(a_c, abs=2e-3)  # maximum camber at x = a (4-13, 4-14)


def test_naca_mean_line_scales_with_the_lift_coefficient():
    camber = 25.0
    _, y = G.camberline("naca65", camber)
    assert y.max() == pytest.approx(0.05515 * lift_coefficient_from_camber(camber), rel=1e-4)  # Table 4-1 at C_l0 = 1


@pytest.mark.parametrize("profile, kind", [("naca65", "naca65"), ("c4", "circular_arc"), ("c4", "parabolic_arc")])
def test_sections_have_their_maximum_thickness(profile, kind):
    upper, lower, _ = G.section(profile, kind, 30.0, 0.08, a_c=0.4 if kind == "parabolic_arc" else 0.5)
    thickness = np.hypot(*(upper - lower).T)  # laid off normal to the camberline
    assert thickness.max() == pytest.approx(0.08, rel=2e-3)


def test_double_circular_arc_blends_into_its_edge_circles():
    camber, t_c, r0 = 20.0, 0.06, 0.005
    upper, lower, edges = G.section("dca", "circular_arc", camber, t_c, edge_radius=r0)
    assert upper[:, 1].max() - lower[:, 1].max() == pytest.approx(t_c, rel=1e-3)  # thickness at mid-chord
    theta = np.radians(camber)
    centre = np.array([r0 * np.cos(theta / 2), r0 * np.sin(theta / 2)])  # on the camberline, r0 from the leading edge
    for surface in (upper, lower):
        gap = np.min(np.hypot(*(surface - centre).T))
        assert gap == pytest.approx(r0, rel=1e-3)  # each arc touches the edge circle
        end = surface[0]
        assert np.hypot(*(end - centre)) == pytest.approx(r0, rel=1e-6)  # and ends on it


def test_flat_plate_throat_is_the_pitch_times_cos_stagger():
    for stagger in (0.0, 30.0, 55.0):
        assert G.throat_opening_ratio_geometric("c4", "circular_arc", 0.0, stagger, 1e-5, 1.3) == pytest.approx(np.cos(np.radians(stagger)), abs=2e-4)


def test_throats_reproduce_aungiers_constructed_naca65_cascades():
    # Fig. 4-12: Aungier's o/s of constructed NACA 65-series cascades, sigma = 1 (10% thick).
    errors = []
    for stagger, points in THROAT_LINES["figure_4_12"]["stagger_deg"].items():
        for cl0, value in points:
            camber = float(camber_from_lift_coefficient(cl0))
            errors.append(G.throat_opening_ratio_geometric("naca65", "naca65", camber, float(stagger), 0.10, 1.0) - value)
    errors = np.abs(errors)
    assert len(errors) >= 50
    assert np.median(errors) <= 0.002 and errors.max() <= 0.005  # the figure reads to about 0.0035


def test_c4_parabolic_throats_reproduce_figure_4_13_up_to_40_degrees_stagger():
    # Fig. 4-13: constructed C.4 parabolic-arc cascades (a/c = 0.4, sigma = 1). Up to
    # 40 deg stagger they agree to the reading; at 50 and 60 deg and low camber the
    # figure's throats are up to 0.019 wider (see the next test and the docs).
    errors = []
    for stagger, points in THROAT_LINES["figure_4_13"]["stagger_deg"].items():
        if float(stagger) > 40.0:
            continue
        for camber, value in points:
            errors.append(G.throat_opening_ratio_geometric("c4", "parabolic_arc", camber, float(stagger), 0.10, 1.0, a_c=0.4) - value)
    errors = np.abs(errors)
    assert len(errors) >= 40
    assert np.median(errors) <= 0.002 and errors.max() <= 0.004


def test_a_blunter_nose_cannot_open_the_throat():
    # At high stagger the throat runs from one blade's nose region to the next
    # blade's rear; the C.4 profile, thicker toward the leading edge than the
    # NACA 65 (Fig. 4-7), must give the narrower throat for the same camber and
    # stagger. Fig. 4-13 shows the opposite at 50 and 60 deg, which is why those
    # curves are not used as a reference.
    for stagger in (50.0, 60.0):
        for camber in (10.0, 20.0):
            c4 = G.throat_opening_ratio_geometric("c4", "circular_arc", camber, stagger, 0.10, 1.0)
            naca = G.throat_opening_ratio_geometric("naca65", "naca65", camber, stagger, 0.10, 1.0)
            assert c4 < naca


# ------------------------------------------------------------------ dca thickness on other camberlines
@pytest.mark.parametrize("camber", [10.0, 30.0])
def test_circular_arc_thickness_on_a_circular_camberline_matches_the_exact_dca(camber):
    t_c, r0 = 0.06, 0.004
    exact = G.section("dca", "circular_arc", camber, t_c, edge_radius=r0)
    laid = G._circular_arc_thickness_on("circular_arc", camber, t_c, 0.5, r0, 401)
    for a, b in zip(exact[:2], laid[:2]):
        assert np.max(cKDTree(a).query(b)[0]) < 2e-3  # same surfaces to within the camberline-curvature term
    assert G.throat_opening_ratio_geometric("dca", "parabolic_arc", camber, 30.0, t_c, 1.5, 0.5, r0) == pytest.approx(
        G.throat_opening_ratio_geometric("dca", "circular_arc", camber, 30.0, t_c, 1.5, 0.5, r0), abs=2e-3)


def test_dca_follows_a_parabolic_camberline():
    camber, a_c = 20.0, 0.65
    upper, lower, _ = G.section("dca", "parabolic_arc", camber, 0.05, a_c=a_c, edge_radius=0.003)
    mean = 0.5 * (upper + lower)
    x, y = G.camberline("parabolic_arc", camber, a_c)
    assert np.max(cKDTree(np.column_stack([x, y])).query(mean)[0]) < 1e-3
    assert np.hypot(*(upper - lower).T).max() == pytest.approx(0.05, rel=2e-3)


# ------------------------------------------------------------------ shock expansion angle
@pytest.mark.parametrize("camber, t_c, solidity, kappa1", [(10.0, 0.03, 1.3, 62.0), (26.0, 0.08, 1.8, 52.0), (40.0, 0.06, 1.2, 45.0)])
def test_expansion_angle_of_a_double_circular_arc_reproduces_aungiers_construction(camber, t_c, solidity, kappa1):
    stagger = kappa1 - camber / 2.0
    analytic = float(suction_surface_expansion_angle(kappa1, camber, t_c, solidity))
    geometric = G.suction_surface_expansion_geometric("dca", "circular_arc", camber, stagger, t_c, solidity, 0.5, 1e-4)
    assert geometric == pytest.approx(analytic, abs=0.3)  # the edge circle moves the start of the arc slightly


def test_an_aft_loaded_meanline_expands_less_ahead_of_the_shock():
    camber, t_c, solidity, kappa1 = 12.0, 0.04, 1.4, 60.0
    phi = {}
    for a_c in (0.5, 0.6, 0.7):
        stagger = kappa1 - float(camberline_angles(camber, a_c)[0])
        phi[a_c] = G.suction_surface_expansion_geometric("dca", "parabolic_arc", camber, stagger, t_c, solidity, a_c, 0.002)
    assert phi[0.5] > phi[0.6] > phi[0.7] > 0.0


# ------------------------------------------------------------------ multiple circular arc
def test_mca_meanline_with_equal_turning_rates_is_the_circular_arc():
    x, y, kappa_t, chi1 = G.mca_meanline(30.0, 0.4, 1.0)
    xc, yc = G.camberline("circular_arc", 30.0)
    assert chi1 == pytest.approx(15.0, abs=1e-9)
    assert np.max(np.abs(y - np.interp(x, xc, yc))) < 1e-9


def test_mca_meanline_with_a_straight_front():
    x, y, kappa_t, chi1 = G.mca_meanline(12.0, 0.6, 0.0)
    assert kappa_t == pytest.approx(chi1, abs=1e-9)  # no turning ahead of the transition point
    front = x <= 0.6
    slope = np.degrees(np.arctan2(np.diff(y[front]), np.diff(x[front])))
    assert np.ptp(slope) < 1e-6


# NASA TP-1338 Table III(a), rotor 35 (validation/cases/nasa_stage35): KIC, KOC, TURN RATE, ZI, ZTC, ZO -> KTC, SETTING ANGLE.
ROTOR35 = [
    (62.55, 53.21, -0.022, 0.698, 2.379, 3.308, 62.99, 61.25),
    (56.16, 44.26, 0.180, 0.280, 1.896, 3.701, 54.31, 52.30),
    (51.69, 25.70, 0.376, 0.000, 1.520, 4.118, 46.24, 41.50),
]


@pytest.mark.parametrize("kic, koc, turn, zi, ztc, zo, ktc, setting", ROTOR35)
def test_mca_meanline_reproduces_rotor_35_sections(kic, koc, turn, zi, ztc, zo, ktc, setting):
    """With the transition point located from ZTC, the meanline returns the printed KTC and setting angle."""
    from scipy.optimize import brentq

    camber, fraction = kic - koc, (ztc - zi) / (zo - zi)

    def axial(c):
        x, y, _, chi1 = G.mca_meanline(camber, c, turn, 2001)
        g = np.radians(kic - chi1)
        a = x * np.cos(g) - y * np.sin(g)
        return float(np.interp(fraction, a / a[-1], x)) - c

    c_t = brentq(axial, 0.05, 0.95)
    _, _, kappa_t, chi1 = G.mca_meanline(camber, c_t, turn)
    assert kic - (chi1 - kappa_t) == pytest.approx(ktc, abs=0.15)  # the reports lay the elements on cones
    assert kic - chi1 == pytest.approx(setting, abs=0.2)


@pytest.mark.parametrize("max_thickness_at, transition", [(0.6, 0.4), (0.4, 0.6), (0.5, 0.5)])
def test_mca_surfaces_meet_their_thickness_and_edge_circles(max_thickness_at, transition):
    camber, t_c, r0 = 20.0, 0.06, 0.004
    upper, lower, edges = G.section("mca", "multiple_circular_arc", camber, t_c, edge_radius=r0, transition=transition,
                                    turning_ratio=0.4, max_thickness_at=max_thickness_at)
    assert np.max(cKDTree(lower).query(upper)[0]) == pytest.approx(t_c, rel=2e-3)
    x, y, _, _ = G.mca_meanline(camber, transition, 0.4, 2001)
    k = int(np.argmin(np.abs(x - max_thickness_at)))
    assert np.min(np.hypot(*(upper - [x[k], y[k]]).T)) == pytest.approx(0.5 * t_c, rel=5e-3)
    for surface in (upper, lower):  # the surfaces end on the edge circles
        for end, circle in ((surface[0], edges[:60]), (surface[-1], edges[60:])):
            centre = circle.mean(axis=0)
            assert np.hypot(*(end - centre)) == pytest.approx(r0, rel=1e-3)
    angles = np.degrees(np.unwrap(np.arctan2(np.gradient(upper[:, 1]), np.gradient(upper[:, 0]))))
    assert np.max(np.abs(np.diff(angles))) < 0.5  # tangent where the arcs meet


def test_an_mca_with_a_straight_front_expands_less_ahead_of_the_shock():
    camber, t_c, solidity, kappa1 = 12.0, 0.035, 1.3, 61.0
    phi = {}
    for turn in (1.0, 0.0):
        chi1, _ = G.mca_shape(camber, 0.6, turn)
        phi[turn] = G.suction_surface_expansion_geometric("mca", "multiple_circular_arc", camber, kappa1 - chi1, t_c, solidity,
                                                          edge_radius=0.002, transition=0.6, turning_ratio=turn, max_thickness_at=0.6)
    assert phi[0.0] < 0.6 * phi[1.0]
