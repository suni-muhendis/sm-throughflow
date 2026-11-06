"""Fixed-mass quasi-one-dimensional passage with an internal normal shock.

NACA Report 1135, continuous-flow and normal-shock relations. Effective
area, relative stagnation temperature and inlet state are prescribed.
The downstream boundary is the static pressure before wake mixing.
"""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from sm_throughflow.correlations.aungier import normal_shock_total_pressure_ratio
from validation.passage_shock_candidate import area_mach, area_ratio, static_ratio
from validation.wake_flux_reference import reduce_wake


class PassageDomain(ValueError):
    def __init__(self, reason, **evidence):
        super().__init__(reason)
        self.reason = reason
        self.evidence = evidence


@dataclass(frozen=True)
class Passage:
    stations: np.ndarray
    pressure: np.ndarray
    mach: np.ndarray
    shock_station: float
    shock_mach_before: float
    shock_mach_after: float
    shock_pressure_before: float
    shock_pressure_after: float
    shock_total_ratio: float
    exit_total_pressure: float
    exit_blockage: float
    relative_mass_error: float
    relative_exit_pressure_error: float


def mass_flux(mach, total_temperature, total_pressure, gamma, gas_constant):
    k = (gamma - 1) / 2
    return (total_pressure * np.sqrt(gamma / (gas_constant * total_temperature)) * mach
            * (1 + k * mach**2)**(-(gamma + 1) / (2 * (gamma - 1))))


def attached_displacement(arc, unit_reynolds):
    """One wall, Prandtl flat-plate reference with a one-seventh profile.

    In the constant-edge-speed limit, theta/x = 0.037 Re_x^-1/5 and
    delta*/theta = 9/7. Here the inlet unit Reynolds number sets the scale.
    """
    return (9 / 7) * .037 * np.asarray(arc)**.8 / unit_reynolds**.2


def solve(stations, geometric_area, total_temperature, *, mass, inlet_total_pressure,
          exit_pressure, displacement_area=None, gamma=1.4, gas_constant=287.05):
    """Match a subsonic exit at fixed mass and solve the shock-position inverse.

    Area and temperature prescribe the continuous piecewise-linear map of
    effective area divided by upstream critical area. The normal shock is
    a discontinuity within one station interval. Multiple admissible
    positions and exact sonic degeneracies are reported explicitly.
    """
    x, area, t0 = (np.asarray(v, dtype=float) for v in (stations, geometric_area, total_temperature))
    disp = np.zeros_like(area) if displacement_area is None else np.asarray(displacement_area, dtype=float)
    if (x.ndim != 1 or len(x) < 3 or any(v.shape != x.shape for v in (area, t0, disp))
            or not np.all(np.isfinite((x, area, t0, disp))) or np.any(np.diff(x) <= 0)
            or np.any(area <= 0) or np.any(t0 <= 0) or np.any(disp < 0)
            or not all(np.isfinite(v) and v > 0 for v in (mass, inlet_total_pressure, exit_pressure, gas_constant))
            or not np.isfinite(gamma) or gamma <= 1):
        raise ValueError("finite ordered stations and physical flow and geometry required")
    effective = area - disp
    if np.any(effective <= 0):
        raise PassageDomain("nonpositive_effective_area")
    ideal_p0 = inlet_total_pressure * (t0 / t0[0])**(gamma / (gamma - 1))
    capacity_ratio = effective * mass_flux(1., t0, ideal_p0, gamma, gas_constant) / mass
    weakest = int(np.argmin(capacity_ratio))
    evidence = dict(minimum_ideal_capacity_over_mass=float(capacity_ratio[weakest]),
                    minimum_capacity_station=float(x[weakest]))
    k = (gamma - 1) / 2
    q = mass / effective[-1] / exit_pressure * np.sqrt(gas_constant * t0[-1] / gamma)
    exit_mach = np.sqrt(2 * q**2 / (1 + np.sqrt(1 + 4 * k * q**2)))
    required_ratio = float(exit_pressure / static_ratio(exit_mach, gamma) / ideal_p0[-1])
    evidence.update(required_exit_mach=float(exit_mach), required_total_ratio=required_ratio)
    if capacity_ratio[weakest] < 1 - 1e-12:
        raise PassageDomain("insufficient_isentropic_capacity", **evidence)
    if not exit_mach < 1:
        raise PassageDomain("exit_not_subsonic", **evidence)
    if not 0 < required_ratio < 1 - 1e-12:
        raise PassageDomain("outside_positive_normal_shock_loss", **evidence)

    high = 2.
    while normal_shock_total_pressure_ratio(high, gamma) > required_ratio:
        high *= 2
    ms = brentq(lambda m: normal_shock_total_pressure_ratio(m, gamma) - required_ratio, 1., high)
    target = area_ratio(ms, gamma)
    residual = capacity_ratio - target
    evidence.update(required_shock_mach=float(ms), required_shock_area_ratio=float(target))
    if np.any((np.abs(residual[:-1]) < 1e-12) & (np.abs(residual[1:]) < 1e-12)):
        raise PassageDomain("shock_position_indeterminate_on_flat_interval", **evidence)
    crossings = list(x[1:-1][np.abs(residual[1:-1]) < 1e-12])
    for i in np.flatnonzero(residual[:-1] * residual[1:] < 0):
        if min(abs(residual[i]), abs(residual[i + 1])) > 1e-12:
            crossings.append(x[i] - residual[i] * (x[i + 1] - x[i]) / (residual[i + 1] - residual[i]))
    if not crossings:
        raise PassageDomain("required_shock_area_outside_internal_passage", **evidence)
    valid = sorted(s for s in crossings if np.all(capacity_ratio[x > s] * required_ratio >= 1 - 1e-12))
    if not valid:
        raise PassageDomain("downstream_capacity_after_shock", shock_candidates=sorted(crossings), **evidence)
    if len(valid) != 1:
        raise PassageDomain("multiple_internal_shocks", shock_candidates=valid, **evidence)
    shock_x = valid[0]
    p0_s = np.interp(shock_x, x, t0) / t0[0]
    p0_s = inlet_total_pressure * p0_s**(gamma / (gamma - 1))
    m_after = np.sqrt((1 + k * ms**2) / (gamma * ms**2 - k))
    upstream = x < shock_x
    ratio = np.where(upstream, 1., required_ratio)
    mach = np.array([area_mach(a, gamma, supersonic=bool(up))
                     for a, up in zip(capacity_ratio * ratio, upstream)])
    pressure = ideal_p0 * ratio * static_ratio(mach, gamma)
    mass_error = np.max(np.abs(effective * mass_flux(mach, t0, ideal_p0 * ratio, gamma, gas_constant) / mass - 1))
    return Passage(x, pressure, mach, float(shock_x), float(ms), float(m_after),
                   float(p0_s * static_ratio(ms, gamma)),
                   float(p0_s * required_ratio * static_ratio(m_after, gamma)),
                   required_ratio, float(ideal_p0[-1] * required_ratio), float(disp[-1] / area[-1]),
                   float(mass_error), float(abs(pressure[-1] / exit_pressure - 1)))


def exit_wake(mach, pressure, total_temperature, blockage, *, gamma=1.4, gas_constant=287.05):
    """Reconstruct the same mass defect and conservatively mix at constant area."""
    if not 0 < mach < 1 or not 0 <= blockage < 1:
        raise ValueError("subsonic exit and physical blockage required")
    nodes, weights = np.polynomial.legendre.leggauss(24)
    q = (nodes + 1) / 2
    # Integrate in velocity ratio q, with y/delta = q**7.
    weights = weights * 3.5 * q**6
    k = (gamma - 1) / 2
    edge_t = total_temperature / (1 + k * mach**2)
    edge_u = mach * np.sqrt(gamma * gas_constant * edge_t)
    t = total_temperature - (total_temperature - edge_t) * q**2
    layer_fraction = blockage / np.dot(weights, 1 - q * edge_t / t)
    if layer_fraction >= 1:
        raise PassageDomain("attached_wake_layers_fill_passage", layer_fraction=float(layer_fraction))
    if blockage == 0:
        return reduce_wake([1.], [pressure], [edge_t], [edge_u], [0.],
                           edge_mass_flux=pressure * edge_u / (gas_constant * edge_t),
                           gamma=gamma, gas_constant=gas_constant)
    return reduce_wake(np.r_[layer_fraction * weights, 1 - layer_fraction],
                       np.full(len(q) + 1, pressure), np.r_[t, edge_t],
                       np.r_[edge_u * q, edge_u], np.zeros(len(q) + 1),
                       edge_mass_flux=pressure * edge_u / (gas_constant * edge_t),
                       gamma=gamma, gas_constant=gas_constant)
