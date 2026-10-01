"""Blade sections and cascade throats (Aungier, 2003, chapter 4)."""
import json
from pathlib import Path

import numpy as np
import pytest

from sm_throughflow.correlations import blade_geometry as G
from sm_throughflow.correlations.aungier import camber_from_lift_coefficient, camberline_angles, throat_opening_ratio, lift_coefficient_from_camber

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
