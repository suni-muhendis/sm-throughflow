"""Planar symmetric passage with displacement feedback on a smooth core.

Per unit span the effective area is the prescribed gap minus the two
identical displacement thicknesses. The isentropic area–Mach relation
sets the common edge speed. This is a symmetric channel reference with
an attached laminar layer and prescribed inlet layer state.
"""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from validation.blade_layer_reference import BladeLayer, SEPARATION_HK, march
from validation.passage_shock_candidate import area_mach, static_ratio


class PassageFailure(RuntimeError):
    def __init__(self, reason, iteration, message):
        super().__init__(message)
        self.reason = reason
        self.iteration = iteration


@dataclass(frozen=True)
class PassageSolution:
    mach: np.ndarray
    velocity: np.ndarray
    static_pressure: np.ndarray
    effective_gap: np.ndarray
    layer: BladeLayer
    relative_gap_residual: float
    relative_mass_residual: float
    iterations: int


def _critical_gap(mass_per_span, total_temperature, total_pressure):
    # NASA Glenn, Mass Flow Rate Equations, M=1, dry air with gamma=1.4.
    critical_flux = total_pressure * np.sqrt(1.4 / (287.05 * total_temperature)) / 1.2**3
    return mass_per_span / critical_flux


def _inlet_capacity(gap, theta, hk, total_temperature, total_pressure):
    # With prescribed inlet theta and Hk, the compressible shape law
    # gives A_eff(M)=a-b M². Maximize A_eff M (1+0.2 M²)^(-3).
    a = gap - 2 * theta * hk
    b = 2 * theta * (0.113 * hk + 0.29)
    if a <= 0:
        return 0.
    peak_mach2 = brentq(lambda y: (1 - y) * (a - b * y) - 2 * b * y * (1 + 0.2 * y), 0., 1.)
    return (total_pressure * np.sqrt(1.4 / (287.05 * total_temperature))
            * (a - b * peak_mach2) * np.sqrt(peak_mach2) / (1 + 0.2 * peak_mach2)**3)


def solve(arc, gap, *, mass_per_span, total_temperature, total_pressure,
          theta0, hk0, tolerance=1e-8, max_iterations=80):
    """Find the subsonic fixed point of mass flow and layer displacement.

    The geometric gap is given normal to the flow, in metres, at ordered
    wall arc knots. The result satisfies the mass balance on those knots.
    Exceeding a trial displaced area's sonic capacity is reported as an
    unresolved interaction. It does not establish a converged flow limit.
    """
    arc, gap = np.asarray(arc, dtype=float), np.asarray(gap, dtype=float)
    if (arc.ndim != 1 or arc.size < 2 or arc.shape != gap.shape
            or not np.all(np.isfinite((arc, gap))) or np.any(np.diff(arc) <= 0)
            or np.any(gap <= 0)):
        raise ValueError("ordered stations and positive geometric gaps required")
    if (not all(np.isfinite(v) and v > 0 for v in
                (mass_per_span, total_temperature, total_pressure, tolerance, theta0))
            or not isinstance(max_iterations, int) or max_iterations < 1):
        raise ValueError("positive finite flow, total state, and iteration settings required")
    if not 1 < hk0 < SEPARATION_HK:
        raise ValueError("an attached initial shape is required")
    critical = _critical_gap(mass_per_span, total_temperature, total_pressure)
    if np.any(gap <= critical):
        raise PassageFailure("geometric_capacity", 0,
                             "bare geometry has no strictly subsonic state at the requested mass flow")
    if mass_per_span > _inlet_capacity(gap[0], theta0, hk0, total_temperature, total_pressure):
        raise PassageFailure("prescribed_inlet_capacity", 0,
                             "specified inlet layer and geometry cannot admit the requested mass flow")

    effective = gap.copy()
    for iteration in range(1, max_iterations + 1):
        mach = np.array([area_mach(value / critical) for value in effective])
        temperature = total_temperature / (1 + 0.2 * mach**2)
        speed = mach * np.sqrt(1.4 * 287.05 * temperature)
        pressure = total_pressure * static_ratio(mach)
        try:
            layer = march(arc, speed, theta0=theta0, hk0=hk0, total_temperature=total_temperature,
                          total_pressure=total_pressure)
        except RuntimeError as exc:
            raise PassageFailure("layer_numerical_failure", iteration, str(exc)) from exc
        if layer.separated:
            raise PassageFailure("attached_layer_limit", iteration,
                                 "trial edge reaches zero modeled wall shear")
        displaced = gap - 2 * layer.displacement_thickness
        if np.any(displaced <= critical):
            raise PassageFailure("unresolved_displacement_capacity", iteration,
                                 "trial layer leaves no strictly subsonic effective area")
        gap_residual = float(np.max(np.abs(displaced - effective) / gap))
        flux = pressure / (287.05 * temperature) * speed * displaced
        mass_residual = float(np.max(np.abs(flux / mass_per_span - 1)))
        if max(gap_residual, mass_residual) <= tolerance:
            return PassageSolution(mach, speed, pressure, displaced, layer,
                                   gap_residual, mass_residual, iteration)
        effective = 0.5 * (effective + displaced)
    raise PassageFailure("interaction_numerical_failure", max_iterations,
                         "displacement and mass residuals exceed tolerance")
