"""The streamline-curvature throughflow solution (Aungier, 2003, sections 7.3 to 7.5)."""
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Union

import numpy as np

from .gas import PerfectGas
from .geometry import Annulus, QuasiNormals, SurfaceGeometry, surface_geometry, uniform_flow_fractions
from .quasi_normal import StationFlow, solve_quasi_normal
from .endwall import EndwallBoundaryLayers, EndwallResult
from .rows import BladeRow, ExitGeometry, RowPerformance

Profile = Union[float, Sequence[float]]


def _on_span(values, t):
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == 1:
        return np.full_like(t, values.item())
    return np.interp(t, np.linspace(0.0, 1.0, values.size), values)


@dataclass(frozen=True)
class InletCondition:
    """Absolute total conditions and flow angle on the first quasi-normal.

    Each is a scalar or values at evenly spaced span fractions, hub to shroud.
    The swirl is given either as ``alpha_deg``, the absolute flow angle from
    the meridional direction, or as ``r_c_theta`` (m^2/s), not both.
    """

    P0: Profile
    T0: Profile
    alpha_deg: Optional[Profile] = None
    r_c_theta: Optional[Profile] = None

    def __post_init__(self):
        if self.alpha_deg is not None and self.r_c_theta is not None:
            raise ValueError("give alpha_deg or r_c_theta, not both")


@dataclass
class Convergence:
    iterations: int = 0
    converged: bool = False
    position_change: List[float] = field(default_factory=list)
    velocity_change: List[float] = field(default_factory=list)


@dataclass(frozen=True)
class ThroughflowSolution:
    geometry: SurfaceGeometry
    stations: List[StationFlow]
    rows: List[BladeRow]
    performance: dict
    convergence: Convergence
    blockage: Optional[np.ndarray] = None
    endwall: Optional[EndwallResult] = None


class Throughflow:
    """A streamline-curvature throughflow problem.

    Quasi-normals are numbered along the annulus; a row with ``inlet = q``
    occupies the gap between quasi-normals ``q`` and ``q + 1``, and every other
    gap is a duct. ``stream_surfaces`` counts hub and shroud, so 11 surfaces
    make 10 stream tubes of equal mass flow.
    """

    def __init__(
        self,
        annulus: Annulus,
        quasi_normals: QuasiNormals,
        inlet: InletCondition,
        mass_flow: float,
        rows: Sequence[BladeRow] = (),
        gas: PerfectGas = PerfectGas(),
        stream_surfaces: int = 11,
        curvature: str = "full",
        blockage: Union[float, Sequence[float]] = 1.0,
        endwall: Optional[EndwallBoundaryLayers] = None,
        endwall_relaxation: float = 0.5,
        max_blockage: float = 0.5,
    ):
        self.annulus = annulus
        self.qn = quasi_normals
        self.inlet = inlet
        self.mass_flow = float(mass_flow)
        self.rows = list(rows)
        self.gas = gas
        self.n = int(stream_surfaces)
        self.curvature = curvature
        self.blockage = np.broadcast_to(np.asarray(blockage, dtype=float), (self.qn.count,)).copy()
        self.endwall = endwall
        self.endwall_relaxation = float(endwall_relaxation)
        self.max_blockage = float(max_blockage)
        self._kb = self.blockage.copy()  # the blockage factor in use during a solution
        self.row_at = {}
        for row in self.rows:
            if not 0 <= row.inlet < self.qn.count - 1:
                raise ValueError("row {} needs quasi-normals {} and {}".format(row.name, row.inlet, row.inlet + 1))
            if row.inlet in self.row_at:
                raise ValueError("two rows share the gap after quasi-normal {}".format(row.inlet))
            self.row_at[row.inlet] = row
        if self.n < 3:
            raise ValueError("need at least 3 stream surfaces")

    # ------------------------------------------------------------------ stations
    def _solve_station(self, geo: SurfaceGeometry, q: int, omega: float, I, s, previous: Optional[StationFlow], swirl=None, beta=None, wake=None) -> StationFlow:
        return solve_quasi_normal(
            self.gas,
            y=geo.y[q],
            t=geo.y[q] / geo.y[q, -1],
            r=geo.r[q],
            eps=geo.eps[q],
            phi=geo.phi[q],
            kappa=geo.kappa[q],
            lam=float(self.qn.lam[q]),
            omega=omega,
            I=I,
            s=s,
            mass_flow=self.mass_flow,
            swirl=swirl,
            beta=beta,
            blockage=float(self._kb[q]),
            wake=wake,
            z=geo.z[q],
            wm_guess=None if previous is None else previous.Wm,
        )

    def _inlet_station(self, geo, previous):
        t = geo.y[0] / geo.y[0, -1]
        H = self.gas.enthalpy(_on_span(self.inlet.T0, t))
        s = self.gas.entropy(H, _on_span(self.inlet.P0, t))
        if self.inlet.r_c_theta is not None:
            return self._solve_station(geo, 0, 0.0, H, s, previous, swirl=_on_span(self.inlet.r_c_theta, t))
        alpha = np.radians(_on_span(0.0 if self.inlet.alpha_deg is None else self.inlet.alpha_deg, t))
        return self._solve_station(geo, 0, 0.0, H, s, previous, beta=alpha)

    def _duct_station(self, geo, q, upstream: StationFlow, previous):
        # (7-40) to (7-42): r C_theta, H and s carried along each stream surface.
        return self._solve_station(geo, q, 0.0, upstream.H, upstream.s, previous, swirl=upstream.r * upstream.C_theta)

    def _row_station(self, geo, q, row: BladeRow, upstream: StationFlow, previous, tol=1e-12, max_passes=200, relaxation=0.5):
        """Exit station of a row, iterating the row model with the exit flow it sets.

        A model whose angle and loss depend on the exit flow (deviation on
        W_m2/W_m1, for example) can overshoot from pass to pass, so after the
        first pass its output is under-relaxed; a model that ignores the exit
        flow converges in two passes as before.
        """
        gas, omega = self.gas, row.omega
        I = upstream.H - omega * upstream.r * upstream.C_theta  # (7-43)
        H_rel_in = I + 0.5 * (omega * upstream.r) ** 2
        P_rel_in = gas.pressure(H_rel_in, upstream.s)
        H_rel_out = I + 0.5 * (omega * geo.r[q]) ** 2  # (7-47), (7-48)
        P_rel_ideal = gas.pressure(H_rel_out, upstream.s)
        exit_geometry = ExitGeometry(t=geo.y[q] / geo.y[q, -1], y=geo.y[q], r=geo.r[q], z=geo.z[q])
        station = previous
        applied = None
        for _ in range(max_passes):
            perf: RowPerformance = row.model(upstream, station, exit_geometry)
            angle = np.asarray(perf.exit_angle, dtype=float)
            loss = np.asarray(perf.loss, dtype=float)
            blocked = None if perf.wake_blockage is None else np.asarray(perf.wake_blockage, dtype=float)
            if applied is not None:
                angle = applied[0] + relaxation * (angle - applied[0])
                loss = applied[1] + relaxation * (loss - applied[1])
                if blocked is not None and applied[2] is not None:
                    blocked = applied[2] + relaxation * (blocked - applied[2])
            applied = (angle, loss, blocked)
            if perf.basis == "inlet":
                P_rel_out = P_rel_ideal - loss * (P_rel_in - upstream.P)  # (7-49)
            elif perf.basis == "exit":
                P_exit = upstream.P if station is None else station.P
                P_rel_out = (P_rel_ideal + loss * P_exit) / (1.0 + loss)
            else:
                raise ValueError("unknown loss basis {}".format(perf.basis))
            s_out = gas.entropy(H_rel_out, P_rel_out)
            wake = None if blocked is None else 1.0 - blocked  # (7-6)
            new = self._solve_station(geo, q, omega, I, s_out, station, beta=angle, wake=wake)
            if station is not None and np.max(np.abs(new.Wm - station.Wm)) <= tol * np.max(new.Wm):
                return new, perf
            station = new
        raise RuntimeError("row {} did not converge with its exit flow".format(row.name))

    # --------------------------------------------------------------- repositioning
    def _mass_fraction_positions(self, geo, stations, psi):
        """Fractions t at which each quasi-normal's cumulative mass flow reaches psi (7-54 to 7-56)."""
        t_new = np.empty_like(geo.y)
        for q, st in enumerate(stations):
            y = geo.y[q]
            g = st.wake * geo.r[q] * st.rho * st.Wm * np.cos(geo.eps[q])  # (7-54)
            h = np.diff(y)
            seg = 0.5 * (g[1:] + g[:-1]) * h
            M = np.concatenate([[0.0], np.cumsum(seg)])
            target = psi * M[-1]
            y_new = np.empty_like(y)
            for j, m_target in enumerate(target):
                k = int(np.clip(np.searchsorted(M, m_target) - 1, 0, len(h) - 1))
                dm = m_target - M[k]
                a = 0.5 * (g[k + 1] - g[k]) / h[k]
                b = g[k]
                if abs(a) * h[k] > 1e-12 * abs(b):
                    x = (-b + np.sqrt(max(b * b + 4.0 * a * dm, 0.0))) / (2.0 * a)
                else:
                    x = dm / b
                y_new[j] = y[k] + x
            y_new[0], y_new[-1] = y[0], y[-1]
            t_new[q] = y_new / y[-1]
        return t_new

    def _damping(self, geo, stations, b_star):
        """Novak's under-relaxation factor F (7-57), per point."""
        if self.curvature != "full":
            return np.ones_like(geo.y)
        dm = np.diff(geo.m, axis=0)
        spacing = np.empty_like(geo.m)
        spacing[0], spacing[-1] = dm[0], dm[-1]
        if geo.m.shape[0] > 2:
            spacing[1:-1] = np.minimum(dm[:-1], dm[1:])
        mach_m = np.array([np.minimum(st.Wm / st.a, 0.95) for st in stations])
        ys = geo.y[:, -1:]
        return 1.0 / (1.0 + (1.0 - mach_m ** 2) * ys ** 2 / (b_star * spacing ** 2))

    # ------------------------------------------------------------------- solve
    def solve(self, tol: float = 1e-9, max_iterations: int = 500, b_star: float = 8.0) -> ThroughflowSolution:
        psi = np.linspace(0.0, 1.0, self.n)
        t = uniform_flow_fractions(self.qn, psi)
        stations: List[Optional[StationFlow]] = [None] * self.qn.count
        performance = {}
        conv = Convergence()
        last_move = np.inf
        row_tol = 1e-6
        self._kb = self.blockage.copy()
        endwall_result = None
        if self.endwall is not None:
            self.endwall.reset()
        for iteration in range(1, max_iterations + 1):
            geo = surface_geometry(self.qn, t, self.curvature)
            previous = list(stations)
            for q in range(self.qn.count):
                if q == 0:
                    stations[q] = self._inlet_station(geo, previous[q])
                elif (q - 1) in self.row_at:
                    row = self.row_at[q - 1]
                    stations[q], performance[row.name] = self._row_station(geo, q, row, stations[q - 1], previous[q], tol=row_tol)
                else:
                    stations[q] = self._duct_station(geo, q, stations[q - 1], previous[q])
            t_target = self._mass_fraction_positions(geo, stations, psi)
            move = float(np.max(np.abs(t_target - t)))
            if move > last_move:
                b_star = 0.5 * (b_star + 1.0)  # (7-59)
            last_move = move
            dv = np.inf if previous[0] is None else max(float(np.max(np.abs(a.Wm - b.Wm) / np.max(a.Wm))) for a, b in zip(stations, previous))
            if self.endwall is not None:
                # End-wall boundary layers on the current flow (Aungier chapter 8); K_B = 1 - B (8-77),
                # limited and under-relaxed as Aungier advises for the sequential coupling.
                endwall_result = self.endwall.solve(self, geo, stations, performance)
                target = 1.0 - np.clip(endwall_result.blockage, 0.0, self.max_blockage)
                dv = max(dv, float(np.max(np.abs(target - self._kb))))
                self._kb = self._kb + self.endwall_relaxation * (target - self._kb)
            conv.iterations = iteration
            conv.position_change.append(move)
            conv.velocity_change.append(dv)
            if move <= tol and dv <= tol:
                conv.converged = True
                break
            # Each row's exit flow need only be a little sharper than the outer change.
            row_tol = float(np.clip(0.01 * min(move, dv), 1e-12, 1e-6))
            t = t + self._damping(geo, stations, b_star) * (t_target - t)
        return ThroughflowSolution(geometry=geo, stations=stations, rows=self.rows, performance=performance, convergence=conv,
                                   blockage=self._kb.copy(), endwall=endwall_result)
