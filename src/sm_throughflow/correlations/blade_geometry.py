"""Compressor blade sections and the cascade throat opening (Aungier, 2003, chapter 4).

Profiles: NACA 65-series and C.4 thickness distributions (Table 4-1) laid
normal to the camberline and along its length (section 4.1), and the
double-circular-arc profile (4-22 to 4-26). Camberlines: the NACA a = 1.0
mean line (Table 4-1, scaled by the lift coefficient), the circular arc
(4-7 to 4-10) and the parabolic arc (4-16 to 4-21). The throat o is the
minimum distance between adjacent blades of the staggered cascade
(section 4.9). Lengths are in units of the chord; angles in degrees in the
cascade frame of ``sm_throughflow.correlations``.
"""
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree

from .aungier import camberline_angles, lift_coefficient_from_camber

#: Stations of Table 4-1, percent chord.
NACA65_STATIONS = np.array([0, 0.5, 0.75, 1.25, 2.5, 5, 7.5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100.0])
#: NACA 65-010 thickness t_b/c in percent (twice the half-thickness). Table 4-1
#: prints 3.480 at 2.5% chord; NACA Report 824 gives the half-thickness 1.574,
#: so the thickness there is 3.148 (every other station agrees).
NACA65_010_THICKNESS = np.array([0, 1.544, 1.864, 2.338, 3.148, 4.354, 5.294, 6.080, 7.332, 8.286, 9.006, 9.520, 9.848, 9.992,
                                 9.926, 9.624, 9.060, 8.292, 7.364, 6.312, 5.168, 3.974, 2.770, 1.620, 0.612, 0.0])
NACA65_010_LE_RADIUS = 0.687  # percent chord; scales with (t_b/c)^2 (NACA practice)
#: NACA a = 1.0 mean line for C_l0 = 1, y/c in percent (Table 4-1); symmetric about mid-chord.
NACA_A10_MEANLINE = np.array([0, 0.250, 0.350, 0.535, 0.930, 1.580, 2.120, 2.585, 3.365, 3.980, 4.475, 4.860, 5.150, 5.355,
                              5.475, 5.515, 5.475, 5.355, 5.150, 4.860, 4.475, 3.980, 3.365, 2.585, 1.580, 0.0])
C4_STATIONS = np.array([0, 1.25, 2.5, 5, 7.5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100.0])
#: C.4 thickness t_b/c in percent for a 10% thick blade (Table 4-1).
C4_THICKNESS = np.array([0, 3.30, 4.54, 6.16, 7.24, 8.04, 9.10, 9.66, 10.0, 9.78, 9.14, 8.10, 6.74, 5.08, 3.20, 2.12, 0.0])
C4_LE_RADIUS, C4_TE_RADIUS = 1.20, 0.60  # percent chord at 10% thickness, proportional to t_b/c


# ------------------------------------------------------------------ camberlines
def camberline(kind, camber, a_c=0.5, points=401):
    """Camberline (x, y) from (0, 0) to (1, 0), chord along x, cambered toward +y."""
    theta = np.radians(float(camber))
    if kind == "naca65":
        # (4-6): tan(theta/4) = 0.1103 C_l0 relates the equivalent circular-arc camber to the lift coefficient.
        cl0 = float(lift_coefficient_from_camber(camber, 0.5))
        x = 0.5 * (1.0 - np.cos(np.linspace(0.0, np.pi, points)))
        y = cl0 * PchipInterpolator(NACA65_STATIONS / 100.0, NACA_A10_MEANLINE / 100.0)(x)
        return x, y
    if abs(theta) < 1e-12:
        x = np.linspace(0.0, 1.0, points)
        return x, np.zeros_like(x)
    if kind == "circular_arc":
        radius = 0.5 / np.sin(theta / 2.0)  # (4-7)
        y_c = -radius * np.cos(theta / 2.0)  # (4-8)
        phi = np.linspace(-theta / 2.0, theta / 2.0, points)
        return 0.5 + radius * np.sin(phi), y_c + radius * np.cos(phi)  # (4-9), centred at mid-chord
    if kind == "parabolic_arc":
        tan4 = 4.0 * np.tan(theta)
        b = (np.sqrt(1.0 + tan4 ** 2 * (a_c - a_c ** 2 - 3.0 / 16.0)) - 1.0) / tan4  # (4-19), c = 1
        x = 0.5 * (1.0 - np.cos(np.linspace(0.0, np.pi, points)))
        # (4-16) as a quadratic in y: A y^2 + B y + C = 0, taking the root through (0, 0) and (1, 0).
        A = (1.0 - 2.0 * a_c) ** 2 / (4.0 * b * b)
        B = (1.0 - 2.0 * a_c) / b * x - (1.0 - 4.0 * a_c) / (4.0 * b)
        C = x * x - x
        # The root that vanishes with C at the end points, in the cancellation-free form C/q
        # (it is -C/B when A = 0, the circular arc at a/c = 0.5).
        q = -0.5 * (B + np.sign(B) * np.sqrt(np.maximum(B * B - 4.0 * A * C, 0.0)))
        return x, C / q
    raise ValueError("unknown camberline {!r}".format(kind))


# ------------------------------------------------------------------ profiles
def _arc_length(x, y):
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    return s / s[-1]


def _circle(center, radius, points=60):
    phi = np.linspace(0.0, 2.0 * np.pi, points, endpoint=False)
    return np.column_stack([center[0] + radius * np.cos(phi), center[1] + radius * np.sin(phi)])


def section(profile, camberline_kind, camber, t_c, a_c=0.5, edge_radius=None, points=401):
    """Upper (suction) and lower (pressure) surfaces and edge circles of a section, chord 1, unstaggered.

    Returns (upper, lower, edges): arrays of (x, y) points; ``edges`` holds
    points on the leading- and trailing-edge circles.
    """
    if profile == "dca":
        return _double_circular_arc(camber, t_c, edge_radius, points)
    x, y = camberline(camberline_kind, camber, a_c, points)
    s = _arc_length(x, y)
    if profile == "naca65":
        scale = t_c / 0.10
        thickness = scale * PchipInterpolator(np.sqrt(NACA65_STATIONS / 100.0), NACA65_010_THICKNESS / 100.0)(np.sqrt(s))
        r_le, r_te = NACA65_010_LE_RADIUS / 100.0 * scale ** 2, 0.0
    elif profile == "c4":
        scale = t_c / 0.10
        thickness = scale * PchipInterpolator(np.sqrt(C4_STATIONS / 100.0), C4_THICKNESS / 100.0)(np.sqrt(s))
        r_le, r_te = C4_LE_RADIUS / 100.0 * scale, C4_TE_RADIUS / 100.0 * scale
    else:
        raise ValueError("unknown profile {!r}".format(profile))
    # Thickness along the camberline's length, laid off normal to it (section 4.1).
    tx, ty = np.gradient(x, s), np.gradient(y, s)
    norm = np.hypot(tx, ty)
    nx, ny = -ty / norm, tx / norm
    upper = np.column_stack([x + 0.5 * thickness * nx, y + 0.5 * thickness * ny])
    lower = np.column_stack([x - 0.5 * thickness * nx, y - 0.5 * thickness * ny])
    edges = []
    for radius, index, sign in ((r_le, 0, 1.0), (r_te, -1, -1.0)):
        if radius > 0.0:
            t0 = np.array([tx[index], ty[index]]) / norm[index]
            edges.append(_circle(np.array([x[index], y[index]]) + sign * radius * t0, radius))
    return upper, lower, (np.vstack(edges) if edges else np.empty((0, 2)))


def _double_circular_arc(camber, t_c, edge_radius, points):
    """Section 4.6: two circular arcs blended by edge circles of radius r0, chord 1.

    The book builds the lower arc by giving t_b and r0 negative values in
    (4-22 to 4-26); taken literally that makes it tangent to the mirror image
    of the edge circle. Here the lower arc is made tangent, from outside, to
    the same edge circles as the upper arc, centred on the camberline at a
    distance r0 from each end (section 4.6).
    """
    if edge_radius is None or edge_radius <= 0.0:
        raise ValueError("a double-circular-arc section needs its edge radius")
    theta = np.radians(float(camber))
    r0 = float(edge_radius)
    y0 = 0.5 * np.tan(theta / 4.0)  # (4-10), c = 1
    half = 0.5 - r0 * np.cos(theta / 2.0)
    centre_y = r0 * np.sin(theta / 2.0)
    d_u = y0 + 0.5 * t_c - centre_y  # (4-24)
    R_u = (d_u ** 2 - r0 ** 2 + half ** 2) / (2.0 * (d_u - r0))  # (4-26)
    d_l = y0 - 0.5 * t_c - centre_y
    R_l = (d_l ** 2 - r0 ** 2 + half ** 2) / (2.0 * (d_l + r0))  # external tangency: |E - C_L| = R_L + r0

    def arc(R, top, tangent_distance):
        centre = np.array([0.0, top - R])
        # Polar half-angle to the point of tangency with the edge circle (4-22).
        half_angle = np.arcsin(half / tangent_distance)
        phi = np.linspace(-half_angle, half_angle, points)
        return np.column_stack([0.5 + R * np.sin(phi), centre[1] + R * np.cos(phi)])

    upper = arc(R_u, y0 + 0.5 * t_c, R_u - r0)
    lower = arc(R_l, y0 - 0.5 * t_c, R_l + r0)
    edges = np.vstack([_circle(np.array([0.5 - half, centre_y]), r0), _circle(np.array([0.5 + half, centre_y]), r0)])
    return upper, lower, edges


# ------------------------------------------------------------------ throat
def _stagger(points, stagger_deg):
    g = np.radians(stagger_deg)
    rot = np.array([[np.cos(g), -np.sin(g)], [np.sin(g), np.cos(g)]])
    return points @ rot.T


def throat_opening_ratio_geometric(profile, camberline_kind, camber, stagger, t_c, solidity, a_c=0.5, edge_radius=None):
    """o/s from the constructed cascade (section 4.9): the minimum distance between adjacent blades.

    The section is staggered by gamma (axial along x, tangential along y);
    its suction (upper) side faces the next blade, one pitch s = c/sigma
    along +y, whose pressure side and edge circles close the passage.
    """
    upper, lower, edges = section(profile, camberline_kind, camber, t_c, a_c, edge_radius)
    pitch = 1.0 / float(solidity)
    suction = _stagger(np.vstack([upper, edges]), stagger)
    pressure = _stagger(np.vstack([lower, edges]), stagger) + np.array([0.0, pitch])
    distance, _ = cKDTree(suction).query(pressure)
    return float(np.min(distance)) / pitch
