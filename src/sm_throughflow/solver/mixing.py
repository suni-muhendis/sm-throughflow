"""Spanwise mixing as turbulent diffusion between stream surfaces (Gallimore, 1986).

S. J. Gallimore, "Spanwise Mixing in Multistage Axial Flow Compressors: Part
II - Throughflow Calculations Including Mixing", J. Turbomachinery 108 (1986)
10-16. Aungier's analysis (2003, ch. 7) carries H, s and r C_theta unchanged
along each stream surface; this module adds the streamwise change that radial
turbulent mixing causes, so that a station downstream receives

    ds/dm      = [ (1/r) d/dr (r k dT/dr) + Phi ] / (rho T V_m)        (2), (A2.1-A2.3)
    d(rV_t)/dm = r E_theta / (rho V_m)                                 (3) without the blade force
    dH0/dm     = T ds/dm + (V_t/r) d(rV_t)/dm + E_z cos(phi) / rho     (4) without the blade force

with the shear stresses of Appendix 1, sigma_r_theta = mu (dV_t/dr - V_t/r)
(A1.1), sigma_rz = mu dV_z/dr (A1.2), E_theta = (1/r^2) d/dr (r^2
sigma_r_theta) (A1.7), E_z = (1/r) d/dr (r sigma_rz) (A1.8), and the
dissipation Phi = mu [(dV_z/dr)^2 + (dV_t/dr - V_t/r)^2] (A2.3). Gallimore
sets the turbulent Prandtl and Schmidt numbers to one, so mu = rho epsilon and
k = mu c_p. At the end walls there is no mixing: the shear stresses and the
heat flux are zero there (adiabatic walls).

Implementation choices (not in the paper):

- Equation (4) is evaluated in its equivalent conservative form,
  rho V_m dH0/dm = (1/r) d/dr [r (k dT/dr + sigma_r_theta V_t + sigma_rz V_z)],
  which equals T ds/dm + (V_t/r) d(rV_t)/dm + E_z cos(phi)/rho term by term
  (with V_z = V_m cos(phi)) and conserves the total enthalpy flux exactly on
  the stream-surface grid.
- Radial derivatives are taken along the quasi-normal through the
  stream-surface radii, following Gallimore's assumption that stream surfaces
  are close to axial. Fluxes sit midway between stream surfaces; the two wall
  fluxes are zero.
- The increments over a gap use the flow on the upstream station of the gap
  (Gallimore uses the previous overall iteration; the result at convergence
  is the same). Where the explicit step would be unstable the gap is split
  into sub-steps, updating T, V_theta and V_z only to evaluate the next
  fluxes.
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np

from ..correlations.spanwise_mixing import A_DEFAULT, mixing_coefficient_ratio

#: Largest explicit diffusion number epsilon dm / (V_m dr^2) per sub-step.
STABLE_STEP = 0.25


@dataclass
class SpanwiseMixing:
    """A uniform mixing coefficient epsilon (m^2/s) for the whole bladed region.

    ``ratio`` fixes epsilon / (V_z L_s); when it is None the ratio comes from
    Gallimore and Cumpsty's eq. (9) with the stage loss of the current
    solution, as Gallimore did with measured overall performance (Part II,
    p. 14). ``stage_length`` is L_s (m), ``thickness`` the blade thickness t
    (m) that sets the turbulent length scale, ``blade_speed`` the mean blade
    speed U_m (m/s). Mixing acts downstream of quasi-normal ``start``
    (the first blade leading edge); the loss of one stage is the entropy
    rise between quasi-normals ``stage_in`` and ``stage_out`` divided by
    ``stages``, Gallimore's level being uniform through the machine.
    """

    stage_length: float
    thickness: float
    blade_speed: float
    start: int
    stage_in: int
    stage_out: int
    stages: int = 1
    ratio: Optional[float] = None
    A: float = A_DEFAULT
    epsilon: float = 0.0
    used_ratio: float = 0.0

    def update(self, gas, stations) -> float:
        """Set epsilon from the current solution and return it."""
        inlet, exit = stations[self.stage_in], stations[self.stage_out]
        vz = float(np.mean([st.mass_average(st.Wm) for st in stations[self.stage_in:self.stage_out + 1]]))
        if self.ratio is not None:
            ratio = self.ratio
        else:
            # Delta P_L = ideal minus actual static-pressure rise; for the stage this is rho T Delta s
            # (Gibbs, at the mean state), so omega = T Delta s / U_m^2.
            ds = (exit.mass_average(exit.s) - inlet.mass_average(inlet.s)) / self.stages
            T = 0.5 * (inlet.mass_average(inlet.T) + exit.mass_average(exit.T))
            loss = max(T * ds, 0.0) / self.blade_speed ** 2
            ratio = mixing_coefficient_ratio(loss, self.thickness / self.stage_length, vz / self.blade_speed, self.A)
        self.used_ratio = float(ratio)
        self.epsilon = float(ratio * vz * self.stage_length)
        return self.epsilon


def _divergence(r, flux, power):
    """(1/r^p) d/dr (r^p F) at the stream surfaces from fluxes midway between them; zero wall fluxes."""
    rf = 0.5 * (r[1:] + r[:-1])
    g = np.concatenate([[0.0], rf ** power * flux, [0.0]])
    edges = np.concatenate([[r[0]], rf, [r[-1]]])
    width = np.diff(edges)
    return np.diff(g) / (r ** power * width)


def mixing_increments(gas, station, phi, dm, epsilon):
    """Changes of H, s and r C_theta over a gap of length ``dm`` (per stream surface).

    ``station`` is the upstream station of the gap and ``phi`` its
    stream-surface slope; returns (dH, ds, d_rCt).
    """
    zeros = np.zeros_like(station.r)
    if epsilon <= 0.0:
        return zeros, zeros.copy(), zeros.copy()
    r = np.asarray(station.r, dtype=float)
    rho, vm = station.rho, station.Wm
    cos_phi = np.cos(phi)
    T = station.T.astype(float).copy()
    vt = station.C_theta.astype(float).copy()
    vz = vm * cos_phi
    dr = np.diff(r)
    lam = epsilon * np.max(dm / np.maximum(vm, 1e-9)) / np.min(dr) ** 2
    steps = max(1, int(np.ceil(lam / STABLE_STEP)))
    h = dm / steps
    dH, ds, drct = zeros.copy(), zeros.copy(), zeros.copy()
    mu_f = epsilon * 0.5 * (rho[1:] + rho[:-1])
    for _ in range(steps):
        rf = 0.5 * (r[1:] + r[:-1])
        vt_f, vz_f = 0.5 * (vt[1:] + vt[:-1]), 0.5 * (vz[1:] + vz[:-1])
        dT = np.diff(T) / dr
        strain = np.diff(vt) / dr - vt_f / rf
        dvz = np.diff(vz) / dr
        q = mu_f * gas.cp * dT                       # k dT/dr, Pr_t = 1
        tau_t = mu_f * strain                        # (A1.1)
        tau_z = mu_f * dvz                           # (A1.2)
        heat = _divergence(r, q, 1)                  # (A2.2)
        E_t = _divergence(r, tau_t, 2)               # (A1.7)
        E_z = _divergence(r, tau_z, 1)               # (A1.8)
        energy = _divergence(r, q + tau_t * vt_f + tau_z * vz_f, 1)
        # Dissipation (A2.3) at the stream surfaces, from the face values on either side.
        diss_f = mu_f * (dvz ** 2 + strain ** 2)
        w = np.concatenate([[0.0], 0.5 * (r[1:] - r[:-1]), [0.0]])
        dsum = np.concatenate([[0.0], diss_f, [0.0]])
        Phi = (dsum[1:] * w[1:] + dsum[:-1] * w[:-1]) / (w[1:] + w[:-1])
        flux = rho * vm
        step_s = h * (heat + Phi) / (flux * T)       # (2)
        step_rct = h * r * E_t / flux                # (3)
        step_H = h * energy / flux                   # (4), conservative form
        ds += step_s
        drct += step_rct
        dH += step_H
        # Local state for the next sub-step's fluxes only.
        dvt = step_rct / r
        dvz_step = h * E_z / flux
        T = T + (step_H - vt * dvt - vz * dvz_step) / gas.cp
        vt = vt + dvt
        vz = vz + dvz_step
    return dH, ds, drct
