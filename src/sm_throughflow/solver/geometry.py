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

    Three-point differences in the interior and two-point at the ends, as
    Aungier recommends for stability (7-67, 7-70).
    """
    dz = np.diff(z, axis=0)
    dr = np.diff(r, axis=0)
    m = np.vstack([np.zeros((1, z.shape[1])), np.cumsum(np.hypot(dz, dr), axis=0)])
    if z.shape[0] < 2:
        zeros = np.zeros_like(z)
        return m, zeros, zeros
    dz_dm = np.empty_like(z)
    dr_dm = np.empty_like(r)
    phi = np.empty_like(z)
    kappa = np.empty_like(z)
    for j in range(z.shape[1]):
        dz_dm[:, j] = np.gradient(z[:, j], m[:, j], edge_order=1)
        dr_dm[:, j] = np.gradient(r[:, j], m[:, j], edge_order=1)
        phi[:, j] = np.arctan2(dr_dm[:, j], dz_dm[:, j])
        kappa[:, j] = -np.gradient(phi[:, j], m[:, j], edge_order=1)
    return m, phi, kappa


def surface_geometry(qn: QuasiNormals, t: np.ndarray, model: str) -> SurfaceGeometry:
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
    m, phi, kappa = _slope_and_curvature(z, r)
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
