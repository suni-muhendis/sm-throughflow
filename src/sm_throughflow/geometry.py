"""One interpretation of contract geometry for admission and simulation."""
import math

import numpy as np

from .contracts import SPAN_FRACTIONS
from .correlations.aungier import camberline_angles
from .correlations.blade_geometry import mca_shape, section


def passage_vertices(stations):
    """Remove only redundant collinear points on both piecewise-linear walls.

    Canonicalization makes inserting a point on an existing segment independent
    of numerical resolution. A genuine corner on either wall is retained.
    """
    out = []
    for point in stations:
        out.append(point)
        while len(out) >= 3:
            a, b, c = out[-3:]
            f = (b.axial_m - a.axial_m) / (c.axial_m - a.axial_m)
            if not all(abs(getattr(b, key) - (getattr(a, key) + f * (getattr(c, key) - getattr(a, key))))
                       <= 1e-12 * max(abs(getattr(a, key)), abs(getattr(c, key)))
                       for key in ("hub_radius_m", "shroud_radius_m")):
                break
            out.pop(-2)
    return out


def station_grid(design, duct_subdivisions=1):
    """Axial quasi-normals and row inlet indices; rows remain single gaps.

    Wall vertices inside a row remain geometric controls, not extra flow
    stations. surface_geometry constrains the interpolated stream surfaces to
    the original annulus there. There is no internal blade-force solution.
    Refinement subdivides ducts only, without applying a row's work twice.
    """
    vertices = passage_vertices(design.passage.stations)
    for row in design.rows:
        if not vertices[0].axial_m < row.leading_edge_axial_m < row.trailing_edge_axial_m < vertices[-1].axial_m:
            raise ValueError("row {} must lie strictly inside the passage".format(row.row_id))
        # A row has no internal flow state. Do not admit a hidden annulus throat
        # smaller than both edge areas and then imply that capacity was checked.
        nodes = [row.leading_edge_axial_m] + [v.axial_m for v in vertices
                 if row.leading_edge_axial_m < v.axial_m < row.trailing_edge_axial_m] + [row.trailing_edge_axial_m]
        hub = np.interp(nodes, [v.axial_m for v in vertices], [v.hub_radius_m for v in vertices])
        tip = np.interp(nodes, [v.axial_m for v in vertices], [v.shroud_radius_m for v in vertices])
        area = tip**2 - hub**2
        candidates = area.tolist()
        for h, s, dh, ds in zip(hub[:-1], tip[:-1], np.diff(hub), np.diff(tip)):
            quadratic = ds**2 - dh**2
            if quadratic > 0:
                f = -(s*ds-h*dh) / quadratic
                if 0 < f < 1:
                    candidates.append((s+f*ds)**2-(h+f*dh)**2)
        if min(candidates) < min(area[0], area[-1]) * (1-1e-10):
            raise ValueError("row {} has an unresolved interior annulus throat; internal blade-row flow is unsupported".format(row.row_id))
    boundaries = sorted({s.axial_m for s in vertices if not any(
                        r.leading_edge_axial_m < s.axial_m < r.trailing_edge_axial_m for r in design.rows)} |
                        {x for r in design.rows for x in (r.leading_edge_axial_m, r.trailing_edge_axial_m)})
    row_gaps = {(r.leading_edge_axial_m, r.trailing_edge_axial_m) for r in design.rows}
    z = [boundaries[0]]
    for a, b in zip(boundaries, boundaries[1:]):
        count = 1 if (a, b) in row_gaps else duct_subdivisions
        z.extend(np.linspace(a, b, count + 1)[1:].tolist())
    indices = {r.row_id: z.index(r.leading_edge_axial_m) for r in design.rows}
    return vertices, z, indices


GEOMETRY_SPANS = tuple(index / 40 for index in range(41))


def blade_sections(row, stations, span_fractions=SPAN_FRACTIONS):
    """Construct sections from the contract's piecewise-linear span inputs.

    The simulator uses the eleven design nodes. Admission additionally checks
    quarter-interval sections using this same construction, not interpolated
    values of nonlinear derived quantities such as stagger or projected chord.
    """
    vertices = passage_vertices(stations)
    x = 0.5 * (row.leading_edge_axial_m + row.trailing_edge_axial_m)
    z = [s.axial_m for s in vertices]
    hub = float(np.interp(x, z, [s.hub_radius_m for s in vertices]))
    shroud = float(np.interp(x, z, [s.shroud_radius_m for s in vertices]))
    span_fractions = np.asarray(span_fractions, dtype=float)
    def values(name):
        return np.interp(span_fractions, SPAN_FRACTIONS, getattr(row, name))
    k_in, k_out = values("metal_angle_in_deg"), values("metal_angle_out_deg")
    chords, thickness = values("chord_m"), values("thickness_to_chord")
    if row.camberline == "multiple_circular_arc":
        transitions, ratios, thickness_locations = (values(name) for name in
            ("transition_point", "turning_rate_ratio", "max_thickness_location"))
    sign = 1.0 if np.mean(k_in - k_out) > 0.0 else -1.0
    out = []
    for k, span in enumerate(span_fractions):
        camber = sign * (k_in[k] - k_out[k])
        if row.camberline == "multiple_circular_arc":
            shape = dict(transition=transitions[k], turning_ratio=ratios[k],
                         max_thickness_at=thickness_locations[k])
            chi1, a_c = mca_shape(camber, shape["transition"], shape["turning_ratio"])
        else:
            shape, a_c = {}, row.max_camber_location
            chi1 = float(camberline_angles(camber, a_c)[0])
        solidity = chords[k] * row.blade_count / (2.0 * math.pi * (hub + span * (shroud - hub)))
        out.append(dict(camber=camber, stagger=sign * k_in[k] - chi1, solidity=solidity,
                        chi1_over_camber=chi1 / camber, a_c=a_c, t_c=thickness[k], shape=shape,
                        span_fraction=float(span), chord=float(chords[k])))
    return out


def validate_span_trends(row):
    """Provisional v7 scope: monotone or single-extremum span distributions.

    Repeated trend reversals are unsupported, not declared physically impossible.
    This conservative admission rule is not an experimentally calibrated limit.
    """
    for name in ("metal_angle_in_deg", "metal_angle_out_deg", "chord_m", "thickness_to_chord",
                 "transition_point", "turning_rate_ratio", "max_thickness_location"):
        value = getattr(row, name)
        if value is None:
            continue
        delta = np.diff(np.asarray(value, dtype=float))
        meaningful = delta[np.abs(delta) > 1e-10 * max(float(np.max(np.abs(value))), 1.0)]
        if np.count_nonzero(meaningful[1:] * meaningful[:-1] < 0) > 1:
            raise ValueError("unsupported spanwise oscillation in {}; v7 admits at most one trend reversal".format(name))


def _intersects(a, b, self_curve=False):
    """Intersection of the represented line segments, including contact.

    Adjacent segments of one curve share a vertex by definition. No thickness
    floor or unsigned nearest-point distance is used to mask intersections.
    """
    p, p1 = a[:-1], a[1:]
    q, q1 = b[:-1], b[1:]
    overlap = np.all(np.maximum(np.minimum(p, p1)[:, None], np.minimum(q, q1)) <=
                     np.minimum(np.maximum(p, p1)[:, None], np.maximum(q, q1)) + 1e-12, axis=2)
    if self_curve:
        overlap &= np.abs(np.arange(len(p))[:, None] - np.arange(len(q))) > 1
    i, j = np.nonzero(overlap)
    if not len(i):
        return False
    def cross(u, v):
        return u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
    u, v = p1[i] - p[i], q1[j] - q[j]
    c1, c2 = cross(u, q[j] - p[i]), cross(u, q1[j] - p[i])
    c3, c4 = cross(v, p[i] - q[j]), cross(v, p1[i] - q[j])
    return bool(np.any((c1 * c2 <= 0.0) & (c3 * c4 <= 0.0)))


def validate_constructed_section(row, parameters):
    """Reject nonfinite, folded or intersecting sampled cascade surfaces.

    This checks the same 401-point construction used for the throat, including
    its edge circles. It is a discrete geometry check, not a 3-D CAD proof.
    """
    s = parameters
    upper, lower, edges = section(row.profile, row.camberline, s["camber"], s["t_c"],
                                  row.max_camber_location, row.edge_radius_to_chord, **s["shape"])
    if not all(np.all(np.isfinite(v)) for v in (upper, lower, edges)):
        raise ValueError("non-finite constructed blade surface")
    if _intersects(upper, upper, True) or _intersects(lower, lower, True) or _intersects(upper[1:-1], lower[1:-1]):
        raise ValueError("constructed blade surfaces intersect")
    angle = np.radians(s["stagger"])
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    curves = [upper @ rotation.T, lower @ rotation.T]
    # section() concatenates complete 60-point edge circles.
    curves += [circle @ rotation.T for circle in np.split(edges, len(edges) // 60)] if len(edges) else []
    pitch = np.array([0.0, 1.0 / s["solidity"]])
    for a in curves:
        for b in curves:
            if _intersects(a, b + pitch):
                raise ValueError("adjacent constructed blades intersect or close the passage")
