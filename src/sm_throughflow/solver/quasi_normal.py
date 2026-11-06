"""Flow on one quasi-normal: normal momentum and mass (Aungier, 2003, section 7.2)."""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.optimize import brentq

from .gas import PerfectGas
from .errors import SolverError, PhysicalStateError


class ChokedError(SolverError):
    """The mass flow cannot pass the quasi-normal (7-39); not a whole-map choke proof."""

    def __init__(self, message, **evidence):
        super().__init__(message, kind="quasi_normal_capacity", component="quasi_normal",
                         details=dict(physical_choke_established=False, scope="current_iterate_only", **evidence))


@dataclass(frozen=True)
class StationFlow:
    """Converged flow on a quasi-normal, one value per stream surface.

    Velocities are in the absolute frame except ``W_theta``, which is in the
    frame of the row that set this station (``omega``). ``H`` and ``P0``/``T0``
    are absolute total conditions; ``I`` is the rothalpy of that frame.
    """

    t: np.ndarray
    y: np.ndarray
    r: np.ndarray
    eps: np.ndarray
    omega: float
    Wm: np.ndarray
    C_theta: np.ndarray
    W_theta: np.ndarray
    h: np.ndarray
    s: np.ndarray
    H: np.ndarray
    I: np.ndarray
    T: np.ndarray
    P: np.ndarray
    rho: np.ndarray
    a: np.ndarray
    T0: np.ndarray
    P0: np.ndarray
    mass_flow: float
    blockage: float
    z: Optional[np.ndarray] = None
    wake_factor: Optional[np.ndarray] = None
    solver_diagnostics: dict = field(default_factory=dict)

    @property
    def alpha(self):
        """Absolute flow angle from the meridional direction, radians."""
        return np.arctan2(self.C_theta, self.Wm)

    @property
    def beta(self):
        """Flow angle in the station's frame, radians."""
        return np.arctan2(self.W_theta, self.Wm)

    @property
    def mach(self):
        return np.hypot(self.Wm, self.C_theta) / self.a

    @property
    def wake(self) -> np.ndarray:
        """Wake blockage factor K_W = 1 - B_wake on each stream surface (7-6); 1 without wakes."""
        return np.ones_like(self.r) if self.wake_factor is None else self.wake_factor

    @property
    def tube_mass_flows(self) -> np.ndarray:
        """Mass flow of each stream tube between adjacent stream surfaces (trapezoidal in y)."""
        g = self.blockage * self.wake * 2.0 * np.pi * self.r * self.rho * self.Wm * np.cos(self.eps)
        return 0.5 * (g[1:] + g[:-1]) * np.diff(self.y)

    def mass_average(self, values) -> float:
        """Mass-weighted average: each stream tube's mass times the mean of its bounding values.

        Averaging tube by tube keeps the average exactly conserved when every
        stream surface conserves the quantity, whatever the flow profile.
        """
        values = np.asarray(values, dtype=float)
        tubes = self.tube_mass_flows
        return float(np.sum(tubes * 0.5 * (values[1:] + values[:-1])) / np.sum(tubes))


def averaged_total_state(gas: PerfectGas, station: StationFlow):
    """Total temperature and pressure of the mass-averaged total enthalpy and entropy.

    Averaging H and s, the quantities the flow carries, and taking the total
    state from them keeps the averages consistent with the second law: a
    machine with no entropy rise on any stream surface has an averaged
    polytropic efficiency of exactly one.
    """
    H = station.mass_average(station.H)
    s = station.mass_average(station.s)
    return float(gas.temperature(H)), float(gas.pressure(H, s))


def polytropic_efficiency(gas: PerfectGas, inlet: StationFlow, exit: StationFlow) -> float:
    """Total-to-total polytropic efficiency between two stations, from averaged total states.

    For a compressor, (R/cp) ln(P02/P01) / ln(T02/T01); for a turbine the
    reciprocal, so that it is at most one in both.
    """
    T1, P1 = averaged_total_state(gas, inlet)
    T2, P2 = averaged_total_state(gas, exit)
    ratio = (gas.R / gas.cp) * np.log(P2 / P1) / np.log(T2 / T1)
    return float(ratio if T2 > T1 else 1.0 / ratio)


def _cumulative_trapezoid(f, y):
    out = np.zeros_like(f)
    out[1:] = np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(y))
    return out


def solve_quasi_normal(
    gas: PerfectGas,
    y: np.ndarray,
    t: np.ndarray,
    r: np.ndarray,
    eps: np.ndarray,
    phi: np.ndarray,
    kappa: np.ndarray,
    lam: float,
    omega: float,
    I: np.ndarray,
    s: np.ndarray,
    mass_flow: float,
    swirl: Optional[np.ndarray] = None,
    beta: Optional[np.ndarray] = None,
    blockage: float = 1.0,
    wake: Optional[np.ndarray] = None,
    z: Optional[np.ndarray] = None,
    wm_guess: Optional[np.ndarray] = None,
    tol: float = 1e-12,
    max_inner: int = 200,
) -> StationFlow:
    """Solve (7-34) in u=Wm**2, with the hub value set by mass flow (7-5).

    Exactly one of ``swirl`` (r C_theta, known downstream of a duct) or
    ``beta`` (the flow angle in the ``omega`` frame, known at a blade-row exit)
    is given. ``I`` is the rothalpy in the ``omega`` frame and ``s`` the
    entropy on each stream surface. Multiplying (7-34) by 2 Wm gives
    u' = 2 f1 u + 2 f2 sqrt(u) + 2 f3 (f2=0 for prescribed swirl).
    This removes the lagged 1/Wm singularity without clipping velocities or
    changing the continuous momentum equation. The integrating factor and
    trapezoid rule now act on u; this is a versioned discretization change.
    ``blockage`` is the end-wall factor K_B of the whole
    quasi-normal and ``wake`` the wake factor K_W on each stream surface, both
    in the mass integral (7-5).
    """
    if (swirl is None) == (beta is None):
        raise ValueError("give exactly one of swirl or beta")
    I = np.asarray(I, dtype=float)
    s = np.asarray(s, dtype=float)
    k_w = np.ones_like(np.asarray(r, dtype=float)) if wake is None else np.asarray(wake, dtype=float)
    H_rel = I + 0.5 * (omega * r) ** 2  # (7-37)
    dI_dy = np.gradient(I, y, edge_order=2)
    ds_dy = np.gradient(s, y, edge_order=2)
    dphi_dy = np.gradient(phi, y, edge_order=2)
    cos_eps, sin_eps = np.cos(eps), np.sin(eps)
    if swirl is not None:
        r_c_theta = np.asarray(swirl, dtype=float)
        d_rct_dy = np.gradient(r_c_theta, y, edge_order=2)
    else:
        tan_b = np.tan(np.asarray(beta, dtype=float))
        cos2_b = np.cos(beta) ** 2
        d_rtanb_dy = np.gradient(r * tan_b, y, edge_order=2)
        f2 = -2.0 * omega * np.cos(beta) * np.sin(beta) * np.cos(lam)  # (7-20)

    def velocities(Wm):
        if swirl is not None:
            C_theta = r_c_theta / r
            W_theta = C_theta - omega * r
        else:
            W_theta = Wm * tan_b
            C_theta = W_theta + omega * r
        return C_theta, W_theta

    def thermo(Wm):
        C_theta, W_theta = velocities(Wm)
        h = H_rel - 0.5 * (Wm ** 2 + W_theta ** 2)  # (7-38)
        return C_theta, W_theta, h

    profile_info = {}

    def profile(wm_hub, start):
        """Wm on every stream surface for a hub value; None if the state is impossible."""
        Wm = start * (wm_hub / start[0])
        change = float("inf")
        for iteration in range(1, max_inner + 1):
            if np.any(Wm <= 0.0):
                return None
            C_theta, W_theta, h = thermo(Wm)
            if np.any(h <= 0.0):
                return None
            T = gas.temperature(h)
            a = gas.sound_speed(h)
            M_m2 = np.minimum((Wm / a) ** 2, 0.9)  # 1 - Mm^2 >= 0.1 (7-30)
            M_t2 = (C_theta / a) ** 2
            dwm_dm_over_wm = (-(1.0 + M_t2) * np.sin(phi) / r - dphi_dy / cos_eps - kappa * np.tan(eps)) / (1.0 - M_m2)  # (7-29)
            if swirl is not None:
                f1 = -kappa * cos_eps + sin_eps * dwm_dm_over_wm  # (7-16)
                f3 = dI_dy - T * ds_dy - (W_theta / r) * d_rct_dy  # (7-18)
            else:
                f1 = cos2_b * (-kappa * cos_eps - (tan_b / r) * d_rtanb_dy + sin_eps * dwm_dm_over_wm)  # (7-19)
                f3 = cos2_b * (dI_dy - T * ds_dy)  # (7-21)
            F = np.exp(_cumulative_trapezoid(2.0 * f1, y))
            forcing = f3 if swirl is not None else f2 * Wm + f3
            square = F * (wm_hub**2 + _cumulative_trapezoid(2.0 * forcing / F, y))
            if np.any(square <= 0.0):
                return None  # no forward-flow solution for this shooting value
            new = np.sqrt(square)
            change = float(np.max(np.abs(new - Wm)) / max(float(np.max(np.abs(new))), 1e-30))
            if not np.all(np.isfinite(new)):
                raise PhysicalStateError("non-finite quasi-normal velocity", component="quasi_normal")
            if change <= tol:
                profile_info.update(iterations=iteration, residual=change, tolerance=tol)
                return new
            Wm = new
        raise SolverError("quasi-normal profile did not converge", component="quasi_normal",
                          iterations=max_inner, residual=change)

    def mass(Wm):
        _, _, h = thermo(Wm)
        rho = gas.density(h, s)
        return blockage * 2.0 * np.pi * np.trapezoid(k_w * r * rho * Wm * cos_eps, y)

    def mean_meridional_mach(Wm):
        _, _, h = thermo(Wm)
        return np.trapezoid(Wm / gas.sound_speed(h), y) / y[-1]

    # Starting shape and hub value.
    if wm_guess is not None and np.all(np.asarray(wm_guess) > 0.0):
        start = np.asarray(wm_guess, dtype=float)
    else:
        rho_t = gas.density(H_rel, s)
        area = 2.0 * np.pi * np.trapezoid(k_w * r * cos_eps, y) * blockage
        start = np.full_like(r, mass_flow / (float(np.mean(rho_t)) * area))

    cache = {}

    def residual(wm_hub):
        Wm = profile(wm_hub, start)
        cache[wm_hub] = Wm
        if Wm is None:
            return None
        return mass(Wm) - mass_flow

    def passes(x):
        """Residual at x, or None when x is beyond the physical or choke limit."""
        f = residual(x)
        if f is None or mean_meridional_mach(cache[x]) >= 1.0:
            return None
        return f

    # Bracket the hub value, starting close to the previous solution when there
    # is one: the step grows geometrically, so a good start costs few solves.
    step = 1.001 if wm_guess is not None else 1.15

    def grow(step):
        return min(step * step, 1.15)

    # A hub value that carries too little mass ...
    lo = float(start[0])
    f_lo = passes(lo)
    recovered_bracket = False
    if f_lo is None:
        # An invalid low-speed profile is not evidence that a smaller hub speed
        # can work: a negative radial enthalpy gradient can require a *larger*
        # hub kinetic energy just to keep the tip flow forward. Search both
        # directions before attempting to bracket mass on the admissible branch.
        recovered_bracket = True
        if swirl is not None:
            thermal_ceiling = np.sqrt(max(2 * H_rel[0] - (r_c_theta[0]/r[0]-omega*r[0])**2, 0.0))
        else:
            thermal_ceiling = np.sqrt(max(2 * H_rel[0] * cos2_b[0], 0.0))
        origin = lo
        tried = {lo}
        for k in range(1, 161):
            factor = 1.15 ** k
            candidates = (min(origin * factor, thermal_ceiling * (1-1e-10)), origin / factor)
            for candidate in candidates:
                if candidate <= 0 or candidate in tried:
                    continue
                tried.add(candidate)
                value = passes(candidate)
                if value is not None:
                    lo, f_lo = candidate, value
                    break
            if f_lo is not None:
                break
        else:
            raise SolverError("no admissible quasi-normal profile found in bounded two-sided hub-speed search",
                              component="quasi_normal", details={"probe_count": len(tried), "physical_limit_established": False})
    down = step
    while f_lo > 0.0:
        previous_valid, previous_residual = lo, f_lo
        lo /= down
        down = grow(down)
        if lo < 1e-9 * float(start[0]):
            raise SolverError("no forward-flow mass bracket as hub velocity approaches zero", component="quasi_normal")
        f_lo = passes(lo)
        if f_lo is None:
            # The lower admissibility boundary may lie between two probes.
            # Approach it from the valid side; do not jump over a narrow root.
            bad, good = lo, previous_valid
            for _ in range(60):
                mid = .5 * (bad + good)
                value = passes(mid)
                if value is None:
                    bad = mid
                elif value > 0:
                    good, previous_residual = mid, value
                else:
                    lo, f_lo = mid, value
                    break
            else:
                raise SolverError("requested mass below the resolved forward-flow profile branch",
                                  component="quasi_normal", details={"smallest_resolved_mass_kg_s": previous_residual+mass_flow,
                                                                      "physical_limit_established": False})
    # ... and one that carries enough, without passing choke.
    hi = lo
    if f_lo < 0.0:
        up = step
        hi = lo * up
        f_hi = passes(hi)
        while f_hi is not None and f_hi < 0.0:
            lo, f_lo = hi, f_hi
            up = grow(up)
            hi *= up
            f_hi = passes(hi)
        if f_hi is None:
            # Beyond the limit: bisect toward it for a valid value that carries enough.
            bad = hi
            for _ in range(60):
                mid = 0.5 * (lo + bad)
                f_mid = passes(mid)
                if f_mid is None:
                    bad = mid
                elif f_mid < 0.0:
                    lo, f_lo = mid, f_mid
                else:
                    hi, f_hi = mid, f_mid
                    break
            else:
                raise ChokedError("mass flow {:.6g} kg/s cannot pass the quasi-normal".format(mass_flow),
                                  requested_kg_s=mass_flow, last_subsonic_kg_s=f_lo + mass_flow,
                                  limiting_hub_velocity_m_s=lo)
    wm_hub = lo if f_lo == 0.0 else brentq(lambda x: residual(x), lo, hi, xtol=1e-14 * hi, rtol=1e-14, maxiter=200)
    Wm = profile(wm_hub, start)
    if mean_meridional_mach(Wm) >= 1.0:
        raise ChokedError("mass flow {:.6g} kg/s chokes the quasi-normal".format(mass_flow))

    C_theta, W_theta, h = thermo(Wm)
    H = h + 0.5 * (Wm ** 2 + C_theta ** 2)
    return StationFlow(
        t=np.asarray(t, dtype=float),
        y=np.asarray(y, dtype=float),
        r=np.asarray(r, dtype=float),
        eps=np.asarray(eps, dtype=float),
        omega=float(omega),
        Wm=Wm,
        C_theta=C_theta,
        W_theta=W_theta,
        h=h,
        s=s,
        H=H,
        I=H - omega * r * C_theta,
        T=gas.temperature(h),
        P=gas.pressure(h, s),
        rho=gas.density(h, s),
        a=gas.sound_speed(h),
        T0=gas.temperature(H),
        P0=gas.pressure(H, s),
        mass_flow=float(mass(Wm)),
        blockage=float(blockage),
        z=None if z is None else np.asarray(z, dtype=float),
        wake_factor=None if wake is None else k_w,
        solver_diagnostics=dict(profile_info, mass_relative_residual=abs(float(mass(Wm)) / mass_flow - 1.0),
                                two_sided_bracket_recovery=recovered_bracket,
                                meridional_mach_limit_active=bool(np.any((Wm / gas.sound_speed(h)) ** 2 > 0.9))),
    )
