"""Aungier's end-wall boundary-layer analysis (Aungier, 2003, chapter 8).

Pitch-averaged, axisymmetric three-dimensional integral boundary layers on the
hub and shroud, marched from quasi-normal to quasi-normal along each wall with
the inviscid wall stream surface as the boundary-layer edge. The result is the
end-wall blockage factor K_B of every quasi-normal (8-76, 8-77), which the
throughflow solution uses in its mass balance (7-5). docs/endwall_boundary_layer.md
records the equations and the choices the book leaves open.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Union

import numpy as np

SEPARATION_SHAPE_FACTOR = 2.4  # limit on H, H1 and H2 (section 8.3, 8.4)
MIN_MOMENTUM_REYNOLDS = 250.0  # (8-73)


def sutherland_air(T):
    """Viscosity of air, Pa s, by Sutherland's law (mu = 1.716e-5 Pa s at 273.15 K, S = 110.4 K)."""
    T = np.asarray(T, dtype=float)
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)


# ----------------------------------------------------------- velocity profiles
def meridional_profile(delta_minus_delta1, theta11):
    """Power-law meridional profile V_m/V_me = (y/delta)^n from (delta - delta1*) and theta11 (8-20 to 8-24).

    Returns (n, H1, delta1*, delta), with H1 limited to the separation value 2.4.
    """
    theta = float(theta11)
    ratio = float(delta_minus_delta1) / theta
    # (8-23): (delta - delta1*) / theta11 = 2 H1 / (H1 - 1), which falls as H1 rises;
    # at the separation limit the outer thickness follows from H1 = 2.4 instead.
    H1 = SEPARATION_SHAPE_FACTOR
    if ratio > 2.0 * H1 / (H1 - 1.0):
        H1 = ratio / (ratio - 2.0)
    n = 0.5 * (H1 - 1.0)  # (8-22)
    delta1 = H1 * theta
    return n, H1, delta1, 2.0 * H1 * theta / (H1 - 1.0) + delta1


def tangential_profile(theta12, n, delta):
    """Tangential profile exponent m and (delta2*, theta22, H2) from theta12 (8-21, 8-25, 8-26; 8-28 to 8-32 for m < 0.05).

    theta12 is limited to 0.99 delta / (n + 1) (section 8.8, step 4) and H2 to 2.4.
    """
    theta12 = min(float(theta12), 0.99 * delta / (n + 1.0))
    m = theta12 * (n + 1.0) ** 2 / (delta - theta12 * (n + 1.0))  # (8-21)
    if m < 0.05:
        p = (n + 1.1) * (n + 2.1) * (n + 3.1)
        m = 0.05 + (theta12 / delta - 0.05 / ((n + 1.0) * (n + 1.05))) * p / 6.82  # (8-31)
        delta2 = delta * 20.0 * m / 21.0  # (8-29)
        theta22 = delta * (0.95 * m - 1.684 * m * m)  # (8-30)
        H2 = 20.0 / (21.0 * (0.95 - 1.684 * m))  # (8-32)
        return m, delta2, theta22, H2
    m = min(m, 0.5 * (SEPARATION_SHAPE_FACTOR - 1.0))
    H2 = 2.0 * m + 1.0  # (8-25)
    delta2 = delta * m / (m + 1.0)  # (8-26)
    return m, delta2, delta2 / H2, H2


def theta12_from_exponent(m, n, delta):
    """Inverse of (8-21) for a power-law tangential profile: theta12 = delta m / [(n + 1)(n + m + 1)]."""
    return delta * m / ((n + 1.0) * (n + m + 1.0))


def streamwise_thicknesses(delta1, theta11, delta2, theta22, theta12, beta_e):
    """delta* and theta in the edge-flow direction (8-40, 8-41), with every defect thickness limited to >= 0."""
    c2, s2 = np.cos(beta_e) ** 2, np.sin(beta_e) ** 2
    delta1, theta11, delta2, theta22, theta12 = (max(v, 0.0) for v in (delta1, theta11, delta2, theta22, theta12))
    d_star = delta1 * c2 + delta2 * s2  # (8-40)
    theta = (theta11 + delta1) * c2 * c2 + (theta22 + delta2) * s2 * s2 + 2.0 * (theta12 + delta1) * s2 * c2 - d_star  # (8-41)
    return d_star, theta


def ludwieg_tillmann(H, reynolds_theta):
    """Skin friction c_f = 0.246 exp(-1.561 H) Re_theta^-0.268 (8-36), with H <= 2.4 and Re_theta >= 250."""
    H = min(H, SEPARATION_SHAPE_FACTOR)
    return 0.246 * np.exp(-1.561 * H) * max(reynolds_theta, MIN_MOMENTUM_REYNOLDS) ** -0.268


def blade_force_defect(theta11_mean, staggered_spacing, clearance=0.0):
    """Base blade force defect thickness nu0 = (0.12 g + delta_c/2) x^3 / (1 + x^3), x = 8 theta11/g (8-44)."""
    x3 = (8.0 * theta11_mean / staggered_spacing) ** 3
    return (0.12 * staggered_spacing + 0.5 * clearance) * x3 / (1.0 + x3)


def defect_correction_factor(theta11_mean, staggered_spacing):
    """F = (1/2) x^3 / (1 + x^3), x = 8 theta11/g (8-55)."""
    x3 = (8.0 * theta11_mean / staggered_spacing) ** 3
    return 0.5 * x3 / (1.0 + x3)


# ------------------------------------------------------------------ the march
@dataclass
class WallState:
    """Boundary-layer data on one wall at one quasi-normal (lengths in metres, wall frame)."""

    delta_minus_delta1: float
    theta11: float
    theta12: float
    n: float
    m: float
    H1: float
    H2: float
    delta: float
    delta1: float
    delta2: float
    theta22: float
    wall_speed: float
    c_theta12: float = 0.0  # V_theta,e theta12 = C_theta,e theta12, the same in every frame (8-68), m^2/s
    nu: float = 0.0


@dataclass
class _Edge:
    r: float
    rho: float
    vm: float
    c_theta: float
    P: float
    T: float
    phi: float
    m: float


@dataclass
class EndwallResult:
    blockage: np.ndarray  # B per quasi-normal (8-76)
    hub: List[WallState] = field(default_factory=list)
    shroud: List[WallState] = field(default_factory=list)


class EndwallBoundaryLayers:
    """Hub and shroud boundary layers and the end-wall blockage they cause (Aungier chapter 8).

    ``inlet_blockage`` B on the first quasi-normal is split equally between the
    walls (8-72), with H1 = 1.4 and a 1/7-power tangential profile (section
    8.8). ``hub_speed`` and ``shroud_speed`` give the wall rotation speed
    (rad/s) of each gap between quasi-normals. By default the shroud is
    stationary and the hub is a drum turning at the rotor speed from the first
    rotor's inlet to the last rotor's exit, except under stators with a shroud
    seal on the hub, whose band is stationary. ``viscosity`` is a function of
    temperature.
    """

    def __init__(
        self,
        inlet_blockage: float = 0.02,
        inlet_H1: float = 1.4,
        inlet_m: float = 1.0 / 7.0,
        hub_speed: Optional[Sequence[float]] = None,
        shroud_speed: Optional[Sequence[float]] = None,
        viscosity: Callable = sutherland_air,
        max_passes: int = 50,
        tol: float = 1e-8,
    ):
        self.inlet_blockage = float(inlet_blockage)
        self.inlet_H1 = float(inlet_H1)
        self.inlet_m = float(inlet_m)
        self.hub_speed = hub_speed
        self.shroud_speed = shroud_speed
        self.viscosity = viscosity
        self.max_passes = int(max_passes)
        self.tol = float(tol)
        self._delta_nu: Dict[tuple, float] = {}  # collateral-flow correction per (row, wall), (8-57)

    def reset(self):
        """Forget the force-defect corrections carried between iterations (a new solution starts)."""
        self._delta_nu = {}

    # ------------------------------------------------------------ set-up
    def _wall_speeds(self, flow, wall):
        given = self.hub_speed if wall == "hub" else self.shroud_speed
        gaps = flow.qn.count - 1
        if given is not None:
            speeds = np.asarray(given, dtype=float)
            if speeds.shape != (gaps,):
                raise ValueError("{}_speed needs one value per gap between quasi-normals ({})".format(wall, gaps))
            return speeds
        speeds = np.zeros(gaps)
        rotors = sorted(q for q, row in flow.row_at.items() if row.omega != 0.0)
        if wall == "hub" and rotors:
            speeds[rotors[0]:rotors[-1] + 1] = flow.row_at[rotors[0]].omega
            for q, row in flow.row_at.items():
                seal = getattr(row.model, "seal", None)
                if row.omega == 0.0 and seal is not None and seal.wall == "hub":
                    speeds[q] = 0.0
        return speeds

    @staticmethod
    def _edge(geo, station, q, j):
        return _Edge(r=float(station.r[j]), rho=float(station.rho[j]), vm=float(station.Wm[j]), c_theta=float(station.C_theta[j]),
                     P=float(station.P[j]), T=float(station.T[j]), phi=float(geo.phi[q, j]), m=float(geo.m[q, j]))

    def _state(self, e: _Edge, X, M, T_inv, wall_speed, m_previous):
        """Boundary-layer data at an edge from the conserved quantities.

        X = r rho V_me (delta - delta1*), M = r rho V_me^2 theta11 and
        T_inv = r^2 rho V_me (C_theta,e theta12), which is the same in a rotating
        and a stationary frame (8-68), so the march carries it through jumps.
        """
        mu = float(self.viscosity(e.T))
        v_theta = e.c_theta - wall_speed * e.r
        ve = np.hypot(e.vm, v_theta)
        theta11 = max(M / (e.r * e.rho * e.vm ** 2), MIN_MOMENTUM_REYNOLDS * mu / (e.rho * ve))  # (8-73)
        n, H1, delta1, delta = meridional_profile(X / (e.r * e.rho * e.vm), theta11)
        c_theta12 = T_inv / (e.r ** 2 * e.rho * e.vm)
        if abs(v_theta) > 1e-6 * ve:
            m, delta2, theta22, H2 = tangential_profile(c_theta12 / v_theta, n, delta)
            theta12 = theta12_from_exponent(m, n, delta) if m >= 0.05 else self._theta12_extended(m, n, delta)
            c_theta12 = v_theta * theta12  # changed only where a limit of section 8.8 applied
        else:
            # No tangential edge velocity in this frame: theta12 is undefined, the profile shape
            # carries over and the frame-free product C_theta,e theta12 is kept for downstream.
            m = m_previous
            theta12 = theta12_from_exponent(m, n, delta) if m >= 0.05 else self._theta12_extended(m, n, delta)
            _, delta2, theta22, H2 = tangential_profile(theta12, n, delta)
        return WallState(delta - delta1, theta11, theta12, n, m, H1, H2, delta, delta1, delta2, theta22, wall_speed, c_theta12)

    @staticmethod
    def _theta12_extended(m, n, delta):
        p = (n + 1.1) * (n + 2.1) * (n + 3.1)
        return delta * ((m - 0.05) * 6.82 / p + 0.05 / ((n + 1.0) * (n + 1.05)))  # (8-31) inverted

    def _sources(self, e: _Edge, s: WallState, dvm_dm, f_me, f_theta, nu):
        """Right-hand sides per unit meridional length of (8-5), (8-6) and (8-10)."""
        mu = float(self.viscosity(e.T))
        v_theta = e.c_theta - s.wall_speed * e.r
        ve = np.hypot(e.vm, v_theta)
        beta_e = np.arctan2(v_theta, e.vm)
        d_star, theta = streamwise_thicknesses(s.delta1, s.theta11, s.delta2, s.theta22, s.theta12, beta_e)
        H = min(d_star / theta, SEPARATION_SHAPE_FACTOR) if theta > 0.0 else SEPARATION_SHAPE_FACTOR
        cf = ludwieg_tillmann(H, e.rho * ve * theta / mu)  # (8-36)
        tau_m = 0.5 * cf * e.rho * ve * e.vm  # (8-34)
        tau_theta = 0.5 * cf * e.rho * ve * v_theta  # (8-35)
        E = 0.025 * (H - 1.0)  # (8-43)
        sin_phi = np.sin(e.phi)
        x = e.r * e.rho * ve * E  # (8-5)
        m_src = (-s.delta1 * e.r * e.rho * e.vm * dvm_dm
                 + e.rho * v_theta * sin_phi * (v_theta * (s.delta2 + s.theta22) + 2.0 * s.wall_speed * e.r * s.delta2)
                 + e.r * (tau_m + f_me * nu))  # (8-6)
        t_src = -e.r ** 2 * s.delta1 * f_theta + e.r ** 2 * (tau_theta + f_theta * nu)  # (8-10)
        return np.array([x, m_src, t_src])

    @staticmethod
    def _conserved(e: _Edge, s: WallState):
        return np.array([e.r * e.rho * e.vm * s.delta_minus_delta1, e.r * e.rho * e.vm ** 2 * s.theta11,
                         e.r ** 2 * e.rho * e.vm * s.c_theta12])

    # ------------------------------------------------------------ seal leakage
    @staticmethod
    def _leak_in(e: _Edge, X, M, T_inv, s: WallState, leak, compressor_speed):
        """Inlet corrections for shroud-seal leakage (8-58 to 8-62); leak > 0 flows from discharge to inlet."""
        delta = leak / (2.0 * np.pi * e.r * e.rho * e.vm)  # (8-59)
        v_theta = e.c_theta - s.wall_speed * e.r
        u_leak = 0.5 * e.r * compressor_speed + v_theta - e.c_theta  # (8-61)
        scale = e.r * e.rho * e.vm
        X = X + scale * delta  # (8-58)
        M = M + scale * e.vm * delta  # (8-60), theta11 + Delta
        T_inv = T_inv + e.r * scale * (delta * v_theta - 0.5 * (delta + abs(delta)) * u_leak)  # (8-62)
        return X, M, T_inv

    @staticmethod
    def _leak_out(e: _Edge, X, M, T_inv, s: WallState, leak, compressor_speed):
        """Discharge corrections for shroud-seal leakage (8-63 to 8-66)."""
        delta = leak / (2.0 * np.pi * e.r * e.rho * e.vm)  # (8-63)
        v_theta = e.c_theta - s.wall_speed * e.r
        u_leak = 0.5 * e.r * compressor_speed + v_theta - e.c_theta  # (8-61)
        scale = e.r * e.rho * e.vm
        X = X - scale * delta  # (8-64)
        M = M - scale * e.vm * delta  # (8-65)
        T_inv = T_inv - e.r * scale * (delta * v_theta - 0.5 * (delta - abs(delta)) * u_leak)  # (8-66)
        return X, M, T_inv

    # ------------------------------------------------------------ one wall
    def _march(self, flow, geo, stations, performance, wall):
        j = 0 if wall == "hub" else -1
        speeds = self._wall_speeds(flow, wall)
        edges = [self._edge(geo, st, q, j) for q, st in enumerate(stations)]
        mass_flow = stations[0].mass_flow
        compressor_speed = max((abs(row.omega) for row in flow.rows), default=0.0)

        # Inlet (8-72) and section 8.8: H1, the 1/7 tangential profile, B split between the walls.
        e = edges[0]
        delta1 = 0.5 * self.inlet_blockage * mass_flow / (2.0 * np.pi * e.r * e.rho * e.vm)
        n = 0.5 * (self.inlet_H1 - 1.0)
        theta11 = delta1 / self.inlet_H1
        delta = delta1 * (n + 1.0) / n  # (8-24)
        theta12 = theta12_from_exponent(self.inlet_m, n, delta)
        omega0 = speeds[0]
        X = e.r * e.rho * e.vm * (delta - delta1)
        M = e.r * e.rho * e.vm ** 2 * theta11
        T_inv = e.r ** 2 * e.rho * e.vm * (e.c_theta - omega0 * e.r) * theta12
        state = self._state(e, X, M, T_inv, omega0, self.inlet_m)
        states = [state]

        for q in range(len(stations) - 1):
            e1, e2 = edges[q], edges[q + 1]
            omega_w = speeds[q]
            row = flow.row_at.get(q)
            seal = getattr(row.model, "seal", None) if row is not None else None
            leak = 0.0
            if seal is not None and seal.wall == wall and row.name in performance:
                leak = float((performance[row.name].diagnostics or {}).get("seal_leakage_mass_flow", 0.0))
            s1 = self._state(e1, *self._conserved(e1, states[-1]), omega_w, states[-1].m)
            X1, M1, T1 = self._conserved(e1, s1)
            if leak:
                X1, M1, T1 = self._leak_in(e1, X1, M1, T1, s1, leak, compressor_speed)
                s1 = self._state(e1, X1, M1, T1, omega_w, s1.m)

            dm = e2.m - e1.m
            dvm_dm = (e2.vm - e1.vm) / dm
            rho_bar, vm_bar, r_bar = 0.5 * (e1.rho + e2.rho), 0.5 * (e1.vm + e2.vm), 0.5 * (e1.r + e2.r)
            f_theta = rho_bar * vm_bar / r_bar * (e2.r * e2.c_theta - e1.r * e1.c_theta) / dm  # (8-9)
            c_bar = 0.5 * (e1.c_theta + e2.c_theta)
            f_me = (rho_bar * vm_bar * dvm_dm + (e2.P - e1.P) / dm - np.sin(0.5 * (e1.phi + e2.phi)) / r_bar * rho_bar * c_bar ** 2)  # (8-8)

            blade = None
            if row is not None and row.name in performance and performance[row.name].diagnostics is not None:
                d = performance[row.name].diagnostics
                if "pitch" in d and "stagger" in d:
                    g = float(d["pitch"][j] * np.cos(np.radians(d["stagger"][j])))  # (8-2)
                    clearance = getattr(row.model, "clearance", None)
                    gap = clearance.gap if clearance is not None and clearance.wall == wall else 0.0
                    blade = (g, gap, row)
            key = (row.name if row is not None else q, wall)

            # Predictor (8-74, 8-75): r rho V_me^2 theta11 and r^2 rho V_me V_theta,e theta12 carried over, H1 kept.
            theta11_guess = M1 / (e2.r * e2.rho * e2.vm ** 2)
            X_guess = e2.r * e2.rho * e2.vm * 2.0 * s1.H1 * theta11_guess / (s1.H1 - 1.0)
            s2 = self._state(e2, X_guess, M1, T1, omega_w, s1.m)
            nu = 0.0
            for _ in range(self.max_passes):
                if blade is not None:
                    g, gap, _row = blade
                    theta_bar = 0.5 * (s1.theta11 + s2.theta11)
                    nu0 = blade_force_defect(theta_bar, g, gap)  # (8-44)
                    nu = nu0 + self._delta_nu.get(key, 0.0)  # (8-56)
                src1 = self._sources(e1, s1, dvm_dm, f_me, f_theta, nu)
                src2 = self._sources(e2, s2, dvm_dm, f_me, f_theta, nu)
                new = np.array([X1, M1, T1]) + dm * 0.5 * (src1 + src2)
                s_new = self._state(e2, *new, omega_w, s2.m)
                if blade is not None:
                    # Collateral-flow correction of the force defect (8-45 to 8-57), from the discharge data.
                    g, gap, row_ = blade
                    w_theta2 = e2.c_theta - row_.omega * e2.r
                    w_theta_bar = 0.5 * (e1.c_theta + e2.c_theta) - row_.omega * r_bar
                    v_theta2 = e2.c_theta - omega_w * e2.r
                    xi = (r_bar / e2.r + w_theta_bar * w_theta2 / (vm_bar * e2.vm)) * r_bar * f_theta * dm / (e2.r * e2.rho * e2.vm)  # (8-53)
                    theta_bar = 0.5 * (s1.theta11 + s_new.theta11)
                    F = defect_correction_factor(theta_bar, g)  # (8-55)
                    if abs(xi) > 0.0:
                        residual = v_theta2 * s_new.theta12 - w_theta2 * s_new.theta11
                        self._delta_nu[key] = (self._delta_nu.get(key, 0.0) - residual / xi) * F  # (8-57)
                # Step 6 of section 8.8: converged on theta11, H1 and nu.
                change = max(abs(s_new.theta11 - s2.theta11) / s_new.theta11, abs(s_new.H1 - s2.H1))
                if blade is not None:
                    nu_next = blade_force_defect(0.5 * (s1.theta11 + s_new.theta11), blade[0], blade[1]) + self._delta_nu.get(key, 0.0)
                    change = max(change, abs(nu_next - nu) / blade[0])
                s2 = s_new
                if change <= self.tol:
                    break
            s2.nu = nu
            if leak:
                X2, M2, T2 = self._leak_out(e2, *self._conserved(e2, s2), s2, leak, compressor_speed)
                s2 = self._state(e2, X2, M2, T2, omega_w, s2.m)
                s2.nu = nu
            states.append(s2)
        return edges, states

    # ------------------------------------------------------------ both walls
    def solve(self, flow, geo, stations, performance) -> EndwallResult:
        mass_flow = stations[0].mass_flow
        hub_edges, hub = self._march(flow, geo, stations, performance, "hub")
        shroud_edges, shroud = self._march(flow, geo, stations, performance, "shroud")
        blockage = np.array([
            sum(2.0 * np.pi * e.r * e.rho * e.vm * s.delta1 for e, s in ((he, hs), (se, ss))) / mass_flow  # (8-76)
            for he, hs, se, ss in zip(hub_edges, hub, shroud_edges, shroud)
        ])
        return EndwallResult(blockage=blockage, hub=hub, shroud=shroud)
