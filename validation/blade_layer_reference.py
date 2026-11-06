"""Direct march of a laminar blade layer on a prescribed smooth edge.

Fidkowski, A Coupled Inviscid-Viscous Airfoil Analysis Solver, Revisited,
DOI 10.2514/1.J061341, equations 5, 6, 45–48, 56 and 61. This direct
march covers the attached part of a planar, adiabatic isentropic edge
segment. The caller supplies a finite incoming layer and splits the edge
at shocks. The segment ends at zero wall shear or the end of the input.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from sm_throughflow.solver.endwall import sutherland_air


def _laminar_friction_product(hk):
    # Eq. 56 on the attached branch.
    return 0.0727 * (5.5 - hk)**3 / (hk + 1) - 0.07


SEPARATION_HK = brentq(_laminar_friction_product, 3., 5.)


def _laminar_dissipation_product(hk):
    # Eq. 61 multiplied by Re_theta.
    if hk < 4:
        return 0.00205 * (4 - hk)**5.5 + 0.207
    return -0.0016 * (hk - 4)**2 / (1 + 0.02 * (hk - 4)**2) + 0.207


def stagnation_seed(velocity_gradient, total_temperature, total_pressure):
    """Return the finite (theta, Hk) limit for Ue = K s + O(s²).

    Fidkowski section IV.C. Balancing the terms proportional to 1/s in
    equations 5 and 6 gives 2(2+Hk) D = 3 F, where F = Cf Re_theta and
    D = (2 Cd/H*) Re_theta. The edge is at the total state in the limit.
    """
    if not all(np.isfinite(v) and v > 0 for v in (
        velocity_gradient, total_temperature, total_pressure
    )):
        raise ValueError("positive finite stagnation gradient and total state required")
    hk = brentq(
        lambda h: 2 * (2 + h) * _laminar_dissipation_product(h) - 3 * _laminar_friction_product(h),
        1.5, 2.8,
    )
    nu = sutherland_air(total_temperature) * 287.05 * total_temperature / total_pressure
    theta2 = _laminar_friction_product(hk) * nu / (2 * (2 + hk) * velocity_gradient)
    return float(np.sqrt(theta2)), hk


def march_from_stagnation(arc, velocity, *, total_temperature, total_pressure, rtol=1e-8):
    """Start at the first positive knot using the stagnation limit.

    The first knot must be the known stagnation point. Estimate its slope
    using the quadratic through it and the first two positive knots.
    Refine those knots to check the initialization error.
    """
    arc, velocity = np.asarray(arc, dtype=float), np.asarray(velocity, dtype=float)
    if (arc.ndim != 1 or arc.size < 3 or velocity.shape != arc.shape
            or not np.all(np.isfinite((arc, velocity))) or np.any(np.diff(arc) <= 0)
            or velocity[0] != 0 or np.any(velocity[1:] <= 0)):
        raise ValueError("a zero-speed stagnation knot and ordered positive edge samples are required")
    s1, s2 = arc[1:3] - arc[0]
    slope = (s2 * velocity[1] / s1 - s1 * velocity[2] / s2) / (s2 - s1)
    theta0, hk0 = stagnation_seed(slope, total_temperature, total_pressure)
    return march(arc, velocity, theta0=theta0, hk0=hk0, total_temperature=total_temperature,
                 total_pressure=total_pressure, sample_at=arc[1:], rtol=rtol)


def _kinetic_shape(hk):
    """Eq. 47 and its derivative on the first branch."""
    offset = hk - 4.35
    numerator = 0.0111 * offset**2 - 0.0278 * offset**3
    shape = numerator / (hk + 1) + 1.528 - 0.0002 * (offset * hk)**2
    derivative = (
        (0.0222 * offset - 0.0834 * offset**2) / (hk + 1)
        - numerator / (hk + 1)**2
        - 0.0004 * offset * hk * (offset + hk)
    )
    return shape, derivative


@dataclass(frozen=True)
class BladeLayer:
    arc: np.ndarray
    momentum_thickness: np.ndarray
    displacement_thickness: np.ndarray
    kinematic_shape: np.ndarray
    kinetic_shape: np.ndarray
    reynolds_theta: np.ndarray
    skin_friction: np.ndarray
    dissipation_power_per_span: np.ndarray
    separated: bool


def march(arc, velocity, *, theta0, hk0, total_temperature, total_pressure,
          sample_at=None, rtol=1e-8):
    """Integrate on one shock-free branch with constant edge total state.

    Input distances are wall arc length in metres and velocities are in
    m/s. The first requested sample is the initial-state location. With
    no explicit sample array the edge knots are used. Interior sample
    locations do not affect the edge interpolation or integration steps.
    Dissipation is the cumulative integral of c_D rho_e U_e³ in W/m.
    No transition or reattachment law is implied by zero wall shear.
    """
    arc, velocity = np.asarray(arc, dtype=float), np.asarray(velocity, dtype=float)
    if arc.ndim != 1 or arc.size < 2 or arc.shape != velocity.shape:
        raise ValueError("at least two paired edge samples are required")
    if not np.all(np.isfinite((arc, velocity))) or np.any(np.diff(arc) <= 0):
        raise ValueError("edge samples must be finite and ordered")
    samples = arc if sample_at is None else np.asarray(sample_at, dtype=float)
    if (samples.ndim != 1 or samples.size < 2 or not np.all(np.isfinite(samples))
            or np.any(np.diff(samples) <= 0) or samples[0] < arc[0] or samples[-1] > arc[-1]):
        raise ValueError("requested samples must be ordered within the prescribed edge")
    if not np.all(np.isfinite((theta0, hk0, total_temperature, total_pressure, rtol))):
        raise ValueError("initial state and total conditions must be finite")
    if not (theta0 > 0 and 1 < hk0 < SEPARATION_HK and total_pressure > 0 and rtol > 0):
        raise ValueError("an attached, positive initial layer and pressure are required")
    gamma, gas_constant = 1.4, 287.05
    cp = gamma * gas_constant / (gamma - 1)
    if (velocity[0] < 0 or (velocity[0] == 0 and samples[0] == arc[0])
            or np.any(velocity[1:] <= 0) or total_temperature <= velocity.max()**2 / (2 * cp)):
        raise ValueError("edge velocity and static temperature must be positive")
    edge = PchipInterpolator(arc, velocity)
    edge_slope = edge.derivative()

    def edge_state(x):
        speed = edge(x)
        temperature = total_temperature - speed**2 / (2 * cp)
        density = total_pressure * (temperature / total_temperature)**(cp / gas_constant) / (
            gas_constant * temperature
        )
        mach2 = speed**2 / (gamma * gas_constant * temperature)
        return speed, density, mach2, sutherland_air(temperature)

    def equations(x, state):
        theta2, hk, _ = state
        if theta2 <= 0 or not 1 < hk < 4.35:
            raise RuntimeError(
                f"integration left the regular laminar shape branch at s={x:.8g} m "
                f"(theta²={theta2:.8g}, Hk={hk:.8g})"
            )
        speed, density, mach2, viscosity = edge_state(x)
        theta = np.sqrt(theta2)
        re_theta = density * speed * theta / viscosity
        shape = hk * (1 + 0.113 * mach2) + 0.29 * mach2
        density_shape = (0.064 / (hk - 0.8) + 0.251) * mach2
        kinetic, kinetic_slope = _kinetic_shape(hk)
        cf = _laminar_friction_product(hk) / re_theta
        twice_cd_over_kinetic = _laminar_dissipation_product(hk) / re_theta
        log_speed_gradient = edge_slope(x) / speed
        theta2_gradient = theta * cf - 2 * theta2 * (2 + shape - mach2) * log_speed_gradient
        log_kinetic_gradient = (
            (twice_cd_over_kinetic - 0.5 * cf) / theta
            - (2 * density_shape / kinetic + 1 - shape) * log_speed_gradient
        )
        return (
            theta2_gradient, kinetic / kinetic_slope * log_kinetic_gradient,
            0.5 * twice_cd_over_kinetic * kinetic * density * speed**3,
        )

    def zero_wall_shear(_x, state):
        return SEPARATION_HK - state[1]

    zero_wall_shear.terminal = True
    zero_wall_shear.direction = -1
    spacing = np.diff(arc)
    max_step = float((np.median(spacing) if velocity[0] == 0 else np.min(spacing)) / 4)
    # Near stagnation the source terms have a 1/s scale even though the
    # balanced initial derivative is small. A large explicit first trial
    # can jump outside the regular shape branch before error estimation.
    first_step = min(max_step, float(samples[0] - arc[0]) / 1000) if velocity[0] == 0 else None
    solution = solve_ivp(
        equations, (samples[0], samples[-1]), (theta0**2, hk0, 0.),
        events=zero_wall_shear, rtol=rtol, atol=(theta0**2 * rtol, rtol, rtol),
        max_step=max_step, first_step=first_step, dense_output=True,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    separated = bool(solution.t_events[0].size)
    sampled = samples[samples <= solution.t[-1]]
    if sampled[-1] < solution.t[-1]:
        sampled = np.r_[sampled, solution.t[-1]]
    theta2, hk, dissipation = solution.sol(sampled)
    theta = np.sqrt(theta2)
    speed, density, mach2, viscosity = edge_state(sampled)
    re_theta = density * speed * theta / viscosity
    shape = hk * (1 + 0.113 * mach2) + 0.29 * mach2
    return BladeLayer(sampled, theta, theta * shape, hk, _kinetic_shape(hk)[0],
                      re_theta, _laminar_friction_product(hk) / re_theta,
                      dissipation, separated)
