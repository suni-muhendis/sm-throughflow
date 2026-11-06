"""Geometry constraints independent of a contour's output sampling grid."""
import numpy as np
import pytest

from sm_throughflow.correlations import blade_geometry as G


@pytest.mark.parametrize('camber', [1e-5, 12., 65.])
def test_meanline_matches_independent_circle_equation(camber):
    theta = np.radians(camber)
    radius = .5/np.sin(theta/2.)
    x = np.array([0., .123456789, .5, .73194371, 1.])
    # Stable sagitta difference for the circle through the chord endpoints.
    d = x-.5
    y = (.25-d*d)/(np.sqrt(radius*radius-d*d)+np.sqrt(radius*radius-.25))
    angle = np.arcsin((.5-x)/radius)
    points, tangent = G.mca_meanline_at(x, camber, .371, 1.)
    np.testing.assert_allclose(points[:, 1], y, atol=8e-15, rtol=0.)
    np.testing.assert_allclose(tangent, np.column_stack((np.cos(angle), np.sin(angle))), atol=8e-15, rtol=0.)
    assert G.mca_shape(camber, .371, 1.)[1] == pytest.approx(.5, abs=8e-15)


@pytest.mark.parametrize('transition,ratio', [(.4234567, 0.), (.3712345, .4), (.6234567, 1.9)])
def test_endpoint_angles_join_and_arc_turning_are_exact(transition, ratio):
    camber = 37.
    x, y, kt, ki = G.mca_meanline(camber, transition, ratio, 437)
    points, tangent = G.mca_meanline_at(x.clip(0., 1.), camber, transition, ratio)
    np.testing.assert_allclose(points[:, 1], y, atol=2e-15, rtol=0.)
    angle = np.degrees(np.arctan2(tangent[:, 1], tangent[:, 0]))
    assert angle[0] == pytest.approx(ki, abs=1e-13)
    assert angle[-1] == pytest.approx(ki-camber, abs=1e-13)
    p, t = G.mca_meanline_at([transition-1e-8, transition, transition+1e-8], camber, transition, ratio)
    assert np.degrees(np.arctan2(t[1, 1], t[1, 0])) == pytest.approx(kt, abs=1e-13)
    assert np.max(np.linalg.norm(np.diff(p, axis=0), axis=1)) < 2e-8
    assert np.max(np.linalg.norm(np.diff(t, axis=0), axis=1)) < 2e-8
    _, apex = G.mca_shape(camber, transition, ratio)
    p, t = G.mca_meanline_at([apex-1e-4, apex, apex+1e-4], camber, transition, ratio)
    assert t[1, 1] == pytest.approx(0., abs=2e-15)
    assert p[1, 1] > max(p[0, 1], p[2, 1])


def test_section_enforces_requested_thickness_and_transition_without_snapping():
    camber, transition, ratio, maximum = 31., .4137891, .37, .6732719
    tc, edge = .075, .0023
    upper, lower, circles = G.section('mca', 'multiple_circular_arc', camber, tc,
        edge_radius=edge, transition=transition, turning_ratio=ratio, max_thickness_at=maximum)
    centre, tangent = G.mca_meanline_at([0., maximum, transition, 1.], camber, transition, ratio)
    normal = np.column_stack((-tangent[:, 1], tangent[:, 0]))
    for sign, surface in [(1., upper), (-1., lower)]:
        expected = centre[1]+sign*tc/2.*normal[1]
        distance = np.linalg.norm(surface-expected, axis=1)
        at = int(np.argmin(distance))
        assert distance[at] < 2e-14
        # Both circular segments meet the exact transition normal.
        projection = (surface-centre[2])@tangent[2]
        join = int(np.argmin(abs(projection)))
        assert abs(projection[join]) < 2e-14
        # Edge-circle centres and surface endpoints share the prescribed radii.
        for point, c in [(surface[0], centre[0]+edge*tangent[0]), (surface[-1], centre[-1]-edge*tangent[-1])]:
            assert np.linalg.norm(point-c) == pytest.approx(edge, abs=2e-14)
    np.testing.assert_allclose(circles[:60].mean(axis=0), centre[0]+edge*tangent[0], atol=1e-15)
    np.testing.assert_allclose(circles[60:].mean(axis=0), centre[-1]-edge*tangent[-1], atol=1e-15)


def test_maximum_thickness_position_has_resolved_small_design_response():
    def shape(x):
        return G.section('mca', 'multiple_circular_arc', 30., .07, edge_radius=.002,
                         transition=.417, turning_ratio=.4, max_thickness_at=x)[0]
    centre = .671234567
    base = shape(centre)
    increments = [1e-5, 1e-6, 1e-7]
    response = [(shape(centre+h)-shape(centre-h))/(2*h) for h in increments]
    assert np.max(abs(response[-1])) > .01
    np.testing.assert_allclose(response[0], response[-1], atol=2e-7, rtol=2e-5)
    np.testing.assert_array_equal(base, shape(centre))


def test_zero_camber_has_finite_exact_geometry_and_invalid_x_is_rejected():
    p, t = G.mca_meanline_at([0., .123, 1.], 0.)
    np.testing.assert_array_equal(p[:, 1], 0.)
    np.testing.assert_array_equal(t, [[1., 0.]]*3)
    assert G.mca_shape(0.) == (0., .5)
    with pytest.raises(ValueError, match='chord coordinates'):
        G.mca_meanline_at([-.01, 1.], 30.)
