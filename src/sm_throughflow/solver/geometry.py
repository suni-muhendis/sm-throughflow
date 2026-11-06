"""Annulus, quasi-normals and stream-surface geometry (Aungier, 2003, sections 7.1, 7.4, 7.8)."""
from dataclasses import dataclass
from typing import Sequence, Tuple

import numpy as np

CURVATURE_MODELS = ("full", "linear", "none")


@dataclass(frozen=True)
class Annulus:
    """Hub and shroud contours as polylines of (z, r), z increasing."""

    hub_z: np.ndarray
    hub_r: np.ndarray
    shroud_z: np.ndarray
    shroud_r: np.ndarray

    @classmethod
    def from_points(cls, hub: Sequence[Tuple[float, float]], shroud: Sequence[Tuple[float, float]]) -> "Annulus":
        hub_z, hub_r = (np.asarray(v, dtype=float) for v in zip(*hub))
        shroud_z, shroud_r = (np.asarray(v, dtype=float) for v in zip(*shroud))
        for z in (hub_z, shroud_z):
            if np.any(np.diff(z) <= 0.0):
                raise ValueError("contour z must increase")
        return cls(hub_z, hub_r, shroud_z, shroud_r)

    def hub_radius(self, z):
        return np.interp(z, self.hub_z, self.hub_r)

    def shroud_radius(self, z):
        return np.interp(z, self.shroud_z, self.shroud_r)


@dataclass(frozen=True)
class QuasiNormals:
    """Straight quasi-normals from a hub point to a shroud point.

    ``y`` is measured along a quasi-normal from the hub; ``lam`` is its angle
    to the radial direction, tan(lambda) = (z_h - z_s) / (r_s - r_h) (7-1).
    """

    z_hub: np.ndarray
    r_hub: np.ndarray
    z_shroud: np.ndarray
    r_shroud: np.ndarray

    @classmethod
    def on(cls, annulus: Annulus, z_hub: Sequence[float], z_shroud: Sequence[float] = None) -> "QuasiNormals":
        z_hub = np.asarray(z_hub, dtype=float)
        z_shroud = z_hub.copy() if z_shroud is None else np.asarray(z_shroud, dtype=float)
        if np.any(np.diff(z_hub) <= 0.0) or np.any(np.diff(z_shroud) <= 0.0):
            raise ValueError("quasi-normals must be ordered along the annulus")
        return cls(z_hub, annulus.hub_radius(z_hub), z_shroud, annulus.shroud_radius(z_shroud))

    @property
    def count(self) -> int:
        return self.z_hub.size

    @property
    def length(self) -> np.ndarray:
        return np.hypot(self.z_shroud - self.z_hub, self.r_shroud - self.r_hub)

    @property
    def lam(self) -> np.ndarray:
        return np.arctan2(self.z_hub - self.z_shroud, self.r_shroud - self.r_hub)

    def points(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """(z, r) of the points at fractions ``t[q, j]`` of each quasi-normal's length."""
        z = self.z_hub[:, None] + t * (self.z_shroud - self.z_hub)[:, None]
        r = self.r_hub[:, None] + t * (self.r_shroud - self.r_hub)[:, None]
        return z, r


def uniform_flow_fractions(qn: QuasiNormals, mass_fractions: np.ndarray) -> np.ndarray:
    """Fractions ``t`` along each quasi-normal that split a uniform flow by ``mass_fractions``.

    For uniform flow the mass below a point is proportional to the integral of
    r dy, which along a straight quasi-normal is r_h t + (r_s - r_h) t^2 / 2.
    """
    psi = np.asarray(mass_fractions, dtype=float)
    a = 0.5 * (qn.r_shroud - qn.r_hub)[:, None]
    b = qn.r_hub[:, None]
    total = a + b
    c = -psi[None, :] * total
    with np.errstate(invalid="ignore", divide="ignore"):
        t = np.where(np.abs(a) > 1e-14 * b, (-b + np.sqrt(b * b - 4.0 * a * c)) / (2.0 * a), -c / b)
    t[:, 0], t[:, -1] = 0.0, 1.0
    return t


@dataclass(frozen=True)
class SurfaceGeometry:
    """Stream-surface geometry on the quasi-normal grid, arrays of shape (Q, N)."""

    z: np.ndarray
    r: np.ndarray
    y: np.ndarray
    m: np.ndarray
    phi: np.ndarray
    kappa: np.ndarray
    eps: np.ndarray


def _slope_and_curvature(z: np.ndarray, r: np.ndarray):
    """Slope phi and curvature kappa_m = -dphi/dm along each stream surface (columns).

    V11 differentiates a local parametric quadratic directly. Composing two
    centered first differences would miss the alternating-position mode and
    leave half the true endpoint curvature even as the mesh is refined.
    Three-point one-sided fits close the ends. The parameter is polygonal arc
    length; the speed denominator makes the curvature parameter-independent.
    Smoothly refined paths have second-order accuracy; arbitrary abrupt mesh
    grading or a physical polyline corner need not have that order.
    """
    h = np.hypot(np.diff(z, axis=0), np.diff(r, axis=0))
    if not np.all(np.isfinite(h)) or np.any(h <= 0.):
        raise ValueError("stream-surface segments must have positive finite length")
    m = np.vstack([np.zeros((1, z.shape[1])), np.cumsum(h, axis=0)])
    if z.shape[0] < 2:
        zeros = np.zeros_like(z)
        return m, zeros, zeros
    if z.shape[0] == 2:
        phi = np.broadcast_to(np.arctan2(r[-1]-r[0], z[-1]-z[0]), z.shape).copy()
        return m, phi, np.zeros_like(z)
    phi, kappa = np.empty_like(z), np.empty_like(z)
    for j in range(z.shape[1]):
        dz, dr = (np.gradient(v[:, j], m[:, j], edge_order=2) for v in (z, r))
        ddz, ddr = (2*np.diff(np.diff(v[:, j])/h[:, j])/(h[:-1,j]+h[1:,j]) for v in (z,r))
        ddz, ddr = (np.r_[v[0], v, v[-1]] for v in (ddz, ddr))
        phi[:, j] = np.arctan2(dr, dz)
        kappa[:, j] = -(dz*ddr-dr*ddz)/(dz*dz+dr*dr)**1.5
    return m, phi, kappa


def _contour_geometry(z, r, annulus):
    """Differentiate wall-constrained geometric paths at the flow stations.

    Interior blade-row controls have no solved flow state. The local annulus
    fraction is interpolated between solved stations and each original wall
    vertex is retained. Work/loss are still applied once between blade edges.
    This is an explicit geometric interpolation, not an internal blade-force
    or throat-flow model. Collinear redundant wall controls are removed so that
    their insertion cannot change the discretization.
    """
    controls = []
    for wall_z, wall_r in ((annulus.hub_z, annulus.hub_r), (annulus.shroud_z, annulus.shroud_r)):
        kept = []
        for x, radius in zip(wall_z, wall_r):
            kept.append((x, radius))
            while len(kept) >= 3:
                a, b, c = kept[-3:]
                interpolated = a[1] + (c[1]-a[1]) * (b[0]-a[0]) / (c[0]-a[0])
                if abs(b[1]-interpolated) > 1e-12 * max(abs(a[1]), abs(c[1])):
                    break
                kept.pop(-2)
        controls.extend(x for x, _ in kept)
    m, phi, kappa = (np.empty_like(z) for _ in range(3))
    for j in range(z.shape[1]):
        knots = np.unique(np.r_[z[:, j], [x for x in controls if z[0, j] < x < z[-1, j]]])
        hub, tip = annulus.hub_radius(z[:, j]), annulus.shroud_radius(z[:, j])
        fraction = (r[:, j] - hub) / (tip - hub)
        local = np.interp(knots, z[:, j], fraction)
        path = annulus.hub_radius(knots) + local * (annulus.shroud_radius(knots) - annulus.hub_radius(knots))
        indices = np.searchsorted(knots, z[:, j])
        path[indices] = r[:, j]  # preserve the solved QN coordinates exactly
        values = _slope_and_curvature(knots[:, None], path[:, None])
        for dest, value in zip((m, phi, kappa), values):
            dest[:, j] = value[indices, 0]
    return m, phi, kappa


def surface_geometry(qn: QuasiNormals, t: np.ndarray, model: str, annulus: Annulus = None) -> SurfaceGeometry:
    """Geometry of the stream surfaces at fractions ``t`` under a curvature model.

    ``full`` differentiates every stream surface; ``linear`` takes slope and
    curvature from the hub and shroud surfaces and interpolates them linearly
    in y; ``none`` sets eps = kappa_m = 0 (simple normal equilibrium), keeping
    the true slope for the continuity term (Aungier, 2003, section 7.6).
    """
    if model not in CURVATURE_MODELS:
        raise ValueError("unknown curvature model {}; expected one of {}".format(model, CURVATURE_MODELS))
    z, r = qn.points(t)
    y = t * qn.length[:, None]
    if annulus is None:
        m, phi, kappa = _slope_and_curvature(z, r)
    else:
        m, phi, kappa = _contour_geometry(z, r, annulus)
    lam = qn.lam[:, None]
    if model == "linear":
        phi = phi[:, :1] + t * (phi[:, -1:] - phi[:, :1])
        kappa = kappa[:, :1] + t * (kappa[:, -1:] - kappa[:, :1])
        eps = phi - lam
    elif model == "none":
        kappa = np.zeros_like(kappa)
        eps = np.zeros_like(phi)
    else:
        eps = phi - lam
    return SurfaceGeometry(z=z, r=r, y=y, m=m, phi=phi, kappa=kappa, eps=eps)
