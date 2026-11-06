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
from scipy.optimize import fsolve
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
def camberline(kind, camber, a_c=0.5, points=401, transition=0.5, turning_ratio=1.0):
    """Camberline (x, y) from (0, 0) to (1, 0), chord along x, cambered toward +y.

    ``transition`` and ``turning_ratio`` define the multiple-circular-arc
    meanline (``mca_meanline``); ``a_c`` the parabolic arc.
    """
    if kind == "multiple_circular_arc":
        x, y, _, _ = mca_meanline(camber, transition, turning_ratio, points)
        return x, y
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


# ------------------------------------------------------------------ multiple circular arc
def _arc_end(angle, rate, length):
    """End-point offset of a path whose angle falls at the constant rate d(angle)/ds = -rate (radians)."""
    half_turn = .5*rate*length
    distance = length*np.sinc(half_turn/np.pi)
    return distance*np.cos(angle-half_turn), distance*np.sin(angle-half_turn)


def _mca_solve(theta, transition, turning_ratio):
    """chi1, front and rear path lengths and the rear turning rate of the meanline (radians, chord 1)."""
    def unpack(v):
        chi1, s_f, s_r = v
        return chi1, s_f, s_r, theta / (turning_ratio * s_f + s_r)

    def residual(v):
        chi1, s_f, s_r, rate = unpack(v)
        x_f, y_f = _arc_end(chi1, turning_ratio * rate, s_f)
        x_r, y_r = _arc_end(chi1 - turning_ratio * rate * s_f, rate, s_r)
        return [x_f + x_r - 1.0, y_f + y_r, x_f - transition]

    # Start from the small-camber solution: kappa falls linearly in x at C1 then C2, and its integral over the chord is zero.
    rate0 = theta / (turning_ratio * transition + 1.0 - transition)
    chi10 = turning_ratio * rate0 * (transition - 0.5 * transition ** 2) + 0.5 * rate0 * (1.0 - transition) ** 2
    v, _, _, msg = fsolve(residual, [chi10, transition, 1.0 - transition], full_output=True, xtol=1e-12)
    if np.max(np.abs(residual(v))) > 1e-9 or min(v[1], v[2]) <= 0.0:
        raise ValueError("no multiple-circular-arc meanline for camber {:.4g} deg, transition {:.4g}, turning ratio {:.4g}: {}".format(
            np.degrees(theta), transition, turning_ratio, msg))
    return unpack(v)


def mca_meanline(camber, transition=0.5, turning_ratio=1.0, points=401):
    """Multiple-circular-arc meanline: two arcs of constant turning rate, tangent at the transition point.

    Crouse, NASA TN D-7345 (1974), eqs. (1) to (4) with its inputs c_t/c and
    C1/C2 (printed pp. 4-9), laid out in the plane of the cascade: the angle
    falls at the rate C1 along the front segment and C2 along the rear one,
    ``turning_ratio`` = C1/C2 (1 is a circular arc, 0 a straight front), and
    the transition point projects onto the chord at ``transition`` (c_t/c).
    Returns x, y (from (0, 0) to (1, 0)), and the angles to the chord of the
    meanline at the transition point and at the leading edge (chi1), degrees.
    """
    theta = np.radians(float(camber))
    if abs(theta) < 1e-12:
        x = np.linspace(0.0, 1.0, points)
        return x, np.zeros_like(x), 0.0, 0.0
    chi1, s_f, s_r, rate = _mca_solve(theta, float(transition), float(turning_ratio))
    front_rate = turning_ratio * rate
    kappa_t = chi1 - front_rate * s_f
    x_f, y_f = _arc_end(chi1, front_rate, s_f)
    xy = []
    for sk in np.linspace(0.0, s_f + s_r, points):
        if sk <= s_f:
            xy.append(_arc_end(chi1, front_rate, sk))
        else:
            dx, dy = _arc_end(kappa_t, rate, sk - s_f)
            xy.append((x_f + dx, y_f + dy))
    xy = np.asarray(xy)
    return xy[:, 0], xy[:, 1], float(np.degrees(kappa_t)), float(np.degrees(chi1))


def mca_shape(camber, transition=0.5, turning_ratio=1.0):
    """Leading-edge angle chi1 (deg) and chordwise position a/c of the maximum camber of the meanline."""
    theta = np.radians(float(camber))
    if abs(theta) < 1e-12:
        return 0., .5  # every point has the same height on a straight line
    chi1, s_f, _, rate = _mca_solve(theta, float(transition), float(turning_ratio))
    kappa_t = chi1-turning_ratio*rate*s_f
    # The maximum is the horizontal tangent, not the nearest output sample.
    if kappa_t >= 0.:
        x_f, _ = _arc_end(chi1, turning_ratio*rate, s_f)
        apex = x_f+np.sin(kappa_t)/rate
    else:
        apex = np.sin(chi1)/(turning_ratio*rate)
    return float(np.degrees(chi1)), float(apex)


def mca_meanline_at(x, camber, transition=0.5, turning_ratio=1.0):
    """Exact meanline positions and unit tangents at specified chord coordinates.

    Invert Crouse's constant-turn circular segments analytically: sin(kappa)
    = sin(kappa_start) - C*(x-x_start). This uses the same two-arc construction
    as ``mca_meanline`` but does not snap geometry constraints to a sampling
    grid. The half-angle displacement avoids cancellation at small camber.
    """
    x = np.asarray(x, dtype=float)
    if not np.all(np.isfinite(x)) or np.any((x < 0.) | (x > 1.)):
        raise ValueError('MCA chord coordinates must lie in [0, 1]')
    theta = np.radians(float(camber))
    if abs(theta) < 1e-12:
        return np.stack((x, np.zeros_like(x)), axis=-1), np.stack((np.ones_like(x), np.zeros_like(x)), axis=-1)
    chi1, s_f, _, rate = _mca_solve(theta, float(transition), float(turning_ratio))
    front_rate = turning_ratio*rate
    kappa_t = chi1-front_rate*s_f
    x_f, y_f = _arc_end(chi1, front_rate, s_f)
    front = x <= transition
    start_x, start_y = np.where(front, 0., x_f), np.where(front, 0., y_f)
    start_angle = np.where(front, chi1, kappa_t)
    curvature = np.where(front, front_rate, rate)
    sine = np.sin(start_angle)-curvature*(x-start_x)
    if np.any(np.abs(sine) > 1.+1e-12):
        raise ValueError('MCA meanline is not a chordwise graph')
    angle = np.arcsin(np.clip(sine, -1., 1.))
    y = start_y+(x-start_x)*np.tan(.5*(start_angle+angle))
    return np.stack((x, y), axis=-1), np.stack((np.cos(angle), np.sin(angle)), axis=-1)


def _left(direction):
    return np.array([-direction[1], direction[0]])


def _arc_radius_touching(point, direction, centre, radius, circle_side=1.0):
    """Signed radius rho of the arc through ``point`` with tangent ``direction`` that touches a circle.

    The arc's centre is point + rho * N (N the left normal of ``direction``).
    ``circle_side`` is +1 when the circle lies on the arc's left at the touch
    point, -1 when on its right. At the touch point T the circle's centre is
    T + side * r * N_T and the arc's centre T + rho * N_T, so
    |O - C| = |rho - side * r|, which solves to
    rho = (r^2 - |P - C|^2) / (2 (N . (P - C) + side * r)).
    """
    d = point - centre
    return (radius ** 2 - d @ d) / (2.0 * (_left(direction) @ d + circle_side * radius))


def _arc_centre(point, direction, rho):
    return point + rho * _left(direction)


def _arc_points(point, direction, rho, end, points):
    """Points of the arc through ``point`` (tangent ``direction``, signed radius rho), from ``point`` to ``end``."""
    if abs(rho) > 1e6:
        return np.linspace(point, end, points)
    centre = _arc_centre(point, direction, rho)
    a0 = np.arctan2(*(point - centre)[::-1])
    a1 = np.arctan2(*(end - centre)[::-1])
    sweep = (a1 - a0 + np.pi) % (2.0 * np.pi) - np.pi
    a = a0 + np.linspace(0.0, sweep, points)
    return centre + abs(rho) * np.column_stack([np.cos(a), np.sin(a)])


def _arc_tangent_at(point, direction, rho, at):
    """Unit tangent, oriented like ``direction``, at the point ``at`` of the arc."""
    if abs(rho) > 1e6:
        return direction
    u = at - _arc_centre(point, direction, rho)
    u = u / np.hypot(*u)
    # Centre on the left (rho > 0): counterclockwise; on the right: clockwise.
    return np.array([-u[1], u[0]]) if rho > 0.0 else np.array([u[1], -u[0]])


def _arc_meets_line(point, direction, rho, origin, line):
    """Where the arc meets the line origin + lam * line, nearest ``origin``."""
    if abs(rho) > 1e6:
        u, lam = np.linalg.solve(np.column_stack([direction, -line]), origin - point)
        return origin + lam * line
    d = origin - _arc_centre(point, direction, rho)
    b = d @ line
    roots = -b + np.array([-1.0, 1.0]) * np.sqrt(max(b * b - (d @ d - rho * rho), 0.0))
    return origin + roots[int(np.argmin(np.abs(roots)))] * line


def _arc_touch_point(point, direction, rho, circle, radius):
    """Point where the arc touches the edge circle."""
    if abs(rho) > 1e6:
        return point + ((circle - point) @ direction) * direction
    o = _arc_centre(point, direction, rho)
    return o + abs(rho) * (circle - o) / np.hypot(*(circle - o))


def _multiple_circular_arc(camber, t_c, edge_radius, transition, turning_ratio, max_thickness_at, points):
    """The four-arc multiple-circular-arc section of Crouse (TN D-5437 eqs. 16 to 25; TN D-7345 edge circles).

    Each surface is two circular arcs, tangent where they cross the normal to
    the meanline through its transition point. At the maximum-thickness point
    (chordwise ``max_thickness_at``) each surface lies t/2 from the meanline
    along its normal and parallel to it (eq. 24), and each surface touches the
    edge circles of radius r0, centred on the meanline r0 from its ends. The
    arc through the maximum-thickness point is fixed by that point, its
    direction and the edge circle on its side of the transition; the other
    arc continues from the transition normal to the other edge circle.
    """
    if edge_radius is None or edge_radius <= 0.0:
        raise ValueError("a multiple-circular-arc section needs its edge radius")
    r0 = float(edge_radius)
    centre, tangent = mca_meanline_at([0., max_thickness_at, transition, 1.], camber, transition, turning_ratio)
    le_c = centre[0] + r0 * tangent[0]
    te_c = centre[-1] - r0 * tangent[-1]
    k_m, k_t = 1, 2
    front_first = max_thickness_at <= transition
    surfaces = []
    for side in (1.0, -1.0):  # suction (upper), pressure (lower)
        d_m = tangent[k_m]
        m = centre[k_m] + side * 0.5 * t_c * _left(d_m)
        near, far = (le_c, te_c) if front_first else (te_c, le_c)
        # The edge circles lie inside the section: right of the suction
        # surface (oriented LE to TE), left of the pressure surface.
        rho1 = _arc_radius_touching(m, d_m, near, r0, -side)
        s_t = _arc_meets_line(m, d_m, rho1, centre[k_t], _left(tangent[k_t]))
        d_t = _arc_tangent_at(m, d_m, rho1, s_t)
        rho2 = _arc_radius_touching(s_t, d_t, far, r0, -side)
        end1 = _arc_touch_point(m, d_m, rho1, near, r0)
        end2 = _arc_touch_point(s_t, d_t, rho2, far, r0)
        half = max(points // 3, 20)
        path = np.vstack([_arc_points(m, d_m, rho1, end1, half)[::-1], _arc_points(m, d_m, rho1, s_t, half)[1:],
                          _arc_points(s_t, d_t, rho2, end2, half)[1:]])
        keep = np.concatenate([[True], np.hypot(*np.diff(path, axis=0).T) > 1e-12])  # case 1: the middle arc has no length
        path = path[keep]
        surfaces.append(path if front_first else path[::-1])
    return surfaces[0], surfaces[1], np.vstack([_circle(le_c, r0), _circle(te_c, r0)])


# ------------------------------------------------------------------ profiles
def _arc_length(x, y):
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    return s / s[-1]


def _circle(center, radius, points=60):
    phi = np.linspace(0.0, 2.0 * np.pi, points, endpoint=False)
    return np.column_stack([center[0] + radius * np.cos(phi), center[1] + radius * np.sin(phi)])


def section(profile, camberline_kind, camber, t_c, a_c=0.5, edge_radius=None, points=401, transition=0.5, turning_ratio=1.0,
            max_thickness_at=0.5):
    """Upper (suction) and lower (pressure) surfaces and edge circles of a section, chord 1, unstaggered.

    Returns (upper, lower, edges): arrays of (x, y) points; ``edges`` holds
    points on the leading- and trailing-edge circles.
    """
    if profile == "mca":
        if camberline_kind != "multiple_circular_arc":
            raise ValueError("the mca profile goes with the multiple_circular_arc camberline")
        return _multiple_circular_arc(camber, t_c, edge_radius, transition, turning_ratio, max_thickness_at, points)
    if profile == "dca":
        if camberline_kind == "circular_arc":
            return _double_circular_arc(camber, t_c, edge_radius, points)
        return _circular_arc_thickness_on(camberline_kind, camber, t_c, a_c, edge_radius, points)
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


def _circular_arc_thickness_on(camberline_kind, camber, t_c, a_c, edge_radius, points):
    """The double-circular-arc thickness laid normal to another camberline (section 4.1).

    The thickness is that of the uncambered double-circular-arc section with
    the same t_b/c and edge radius r0 (4-22 to 4-26 at zero camber): two arcs
    of radius R between the edge circles, tangent to them at x_t. It is laid
    off normal to the camberline along its length, as the NACA 65 and C.4
    thicknesses are, and the edge circles sit on the camberline at r0 from
    each end. On a circular-arc camberline the exact construction
    (``_double_circular_arc``) is used instead; this one differs from it only
    by the curvature of the camberline over the half thickness.
    """
    if edge_radius is None or edge_radius <= 0.0:
        raise ValueError("a double-circular-arc section needs its edge radius")
    r0 = float(edge_radius)
    half = 0.5 - r0
    d = 0.5 * t_c
    R = (d ** 2 - r0 ** 2 + half ** 2) / (2.0 * (d - r0))  # (4-26) at zero camber
    x_t = 0.5 - R * half / (R - r0)  # tangency with the edge circle (4-22)
    x, y = camberline(camberline_kind, camber, a_c, points)
    s = _arc_length(x, y)
    keep = (s >= x_t) & (s <= 1.0 - x_t)
    keep[[np.argmax(keep), len(s) - 1 - np.argmax(keep[::-1])]] = True
    thickness = 2.0 * (d - R + np.sqrt(np.maximum(R ** 2 - (s - 0.5) ** 2, 0.0)))
    tx, ty = np.gradient(x, s), np.gradient(y, s)
    norm = np.hypot(tx, ty)
    nx, ny = -ty / norm, tx / norm
    upper = np.column_stack([x + 0.5 * thickness * nx, y + 0.5 * thickness * ny])[keep]
    lower = np.column_stack([x - 0.5 * thickness * nx, y - 0.5 * thickness * ny])[keep]
    edges = []
    for index, sign in ((0, 1.0), (-1, -1.0)):
        t0 = np.array([tx[index], ty[index]]) / norm[index]
        edges.append(_circle(np.array([x[index], y[index]]) + sign * r0 * t0, r0))
    return upper, lower, np.vstack(edges)


# ------------------------------------------------------------------ throat
def _stagger(points, stagger_deg):
    g = np.radians(stagger_deg)
    rot = np.array([[np.cos(g), -np.sin(g)], [np.sin(g), np.cos(g)]])
    return points @ rot.T


def throat_opening_ratio_geometric(profile, camberline_kind, camber, stagger, t_c, solidity, a_c=0.5, edge_radius=None, **shape):
    """o/s from the constructed cascade (section 4.9): the minimum distance between adjacent blades.

    The section is staggered by gamma (axial along x, tangential along y);
    its suction (upper) side faces the next blade, one pitch s = c/sigma
    along +y, whose pressure side and edge circles close the passage.
    ``shape`` passes the multiple-circular-arc parameters to ``section``.
    """
    upper, lower, edges = section(profile, camberline_kind, camber, t_c, a_c, edge_radius, **shape)
    pitch = 1.0 / float(solidity)
    suction = _stagger(np.vstack([upper, edges]), stagger)
    pressure = _stagger(np.vstack([lower, edges]), stagger) + np.array([0.0, pitch])
    distance, _ = cKDTree(suction).query(pressure)
    return float(np.min(distance)) / pitch


def suction_surface_expansion_geometric(profile, camberline_kind, camber, stagger, t_c, solidity, a_c=0.5, edge_radius=None, **shape):
    """Expansion angle phi of the shock model (section 6.7) from the constructed cascade, degrees.

    Aungier's (6-65) to (6-69) take the suction surface as a circular arc
    turning through the whole camber. Here phi is read off the constructed
    section: the turning of the suction surface from where it leaves the
    leading-edge circle to the foot of the normal dropped onto it from the
    adjacent blade's leading edge, the passage shock of the model. For a
    double circular arc this is the book's construction; for a parabolic-arc
    or NACA meanline it follows the actual surface. The individual NASA
    reports' PHISS uses their assumed shock position, which need not coincide
    with this geometric foot; it is not an independent shock measurement.
    """
    leading, foot = suction_surface_shock_angles(profile, camberline_kind, camber, stagger, t_c, solidity,
                                                a_c, edge_radius, **shape)
    return float(max(leading - foot, 0.0))


def suction_surface_shock_angles(profile, camberline_kind, camber, stagger, t_c, solidity, a_c=0.5,
                                 edge_radius=None, **shape):
    """Suction-surface tangent angles at LE and passage-shock foot, degrees from axial.

    Retains Aungier section 6.7's geometric foot (nearest point to adjacent
    LE), continuously on the represented segments. NACA RM E57A30 appendix B uses the ACTUAL incoming flow angle minus
    the foot tangent in the Prandtl-Meyer calculation; the surface turning
    equals that flow turning only for suction-surface-tangent incidence.
    These are cylindrical section angles. Production supplies the complete
    surface too, so the foot is located again in the row-cone metric.
    """
    upper, _, _ = section(profile, camberline_kind, camber, t_c, a_c, edge_radius, **shape)
    suction = _stagger(upper, stagger)
    leading, foot = projected_surface_shock_angles((suction*solidity)[None, :, :], np.array([1.]))
    return float(leading[0]), float(foot[0])


def projected_surface_shock_angles(surfaces, meridional_cosine):
    """LE/foot tangents after projecting the WHOLE surface onto the row cone.

    Surfaces have shape (span, points, 2), in cylindrical pitch units. Axial
    distances stretch by 1/cos(phi); pitch stays circumferential. The foot
    is the closest point on a C1 Hermite interpolant, not the closest sampled
    vertex. Shared tangents avoid polygon-vertex plateaus as the foot moves
    between segments. This retains Aungier's normal-to-surface approximation, not a
    back-pressure-dependent shock-location model or exact developed cone.
    """
    surfaces = np.asarray(surfaces, dtype=float)
    cp = np.asarray(meridional_cosine, dtype=float)
    if (surfaces.ndim != 3 or surfaces.shape[2] != 2 or surfaces.shape[1] < 3
            or cp.shape != (surfaces.shape[0],) or not np.all(np.isfinite(surfaces))
            or not np.all(np.isfinite(cp)) or np.any(cp <= 0) or np.any(cp > 1)):
        raise ValueError("invalid projected shock surface geometry")
    p = surfaces.copy()
    p[:, :, 0] /= cp[:, None]
    segment = np.diff(p, axis=1)
    square = np.sum(segment**2, axis=2)
    if np.any(square <= 0):
        raise ValueError("shock surface contains a zero-length segment")
    h = np.sqrt(square)[:, :, None]
    secant = segment/h
    tangent = np.empty_like(p)
    tangent[:, 1:-1] = (h[:, 1:]*secant[:, :-1]+h[:, :-1]*secant[:, 1:])/(h[:, :-1]+h[:, 1:])
    tangent[:, 0] = ((2*h[:, 0]+h[:, 1])*secant[:, 0]-h[:, 0]*secant[:, 1])/(h[:, 0]+h[:, 1])
    tangent[:, -1] = ((2*h[:, -1]+h[:, -2])*secant[:, -1]-h[:, -1]*secant[:, -2])/(h[:, -1]+h[:, -2])
    c1, end = h*tangent[:, :-1], h*tangent[:, 1:]
    c2, c3 = 3*segment-2*c1-end, -2*segment+c1+end
    u = np.clip(np.sum((np.array([0., 1.])-p[:, :-1])*segment, axis=2)/square, 0., 1.)[:, :, None]
    for _ in range(5):
        distance = p[:, :-1]+u*(c1+u*(c2+u*c3))-np.array([0., 1.])
        d1, d2 = c1+u*(2*c2+3*u*c3), 2*c2+6*u*c3
        denominator = np.sum(d1*d1+distance*d2, axis=2, keepdims=True)
        step = np.divide(np.sum(distance*d1, axis=2, keepdims=True), denominator,
                         out=np.zeros_like(u), where=np.abs(denominator)>1e-30)
        u = np.clip(u-step, 0., 1.)
    distance = p[:, :-1]+u*(c1+u*(c2+u*c3))-np.array([0., 1.])
    index = np.argmin(np.sum(distance**2, axis=2), axis=1)
    derivative = c1+u*(2*c2+3*u*c3)
    j = np.arange(len(p))
    foot = np.arctan2(derivative[j, index, 1], derivative[j, index, 0])
    leading = np.arctan2(tangent[:, 0, 1], tangent[:, 0, 0])
    return np.degrees(leading), np.degrees(foot)
