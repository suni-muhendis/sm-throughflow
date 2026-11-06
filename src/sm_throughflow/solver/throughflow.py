"""The streamline-curvature throughflow solution (Aungier, 2003, sections 7.3 to 7.5)."""
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Union

import numpy as np

from .gas import PerfectGas
from .errors import SolverError, PhysicalStateError
from .geometry import Annulus, QuasiNormals, SurfaceGeometry, surface_geometry, uniform_flow_fractions
from .quasi_normal import StationFlow, solve_quasi_normal
from .endwall import EndwallBoundaryLayers, EndwallResult
from .mixing import SpanwiseMixing, mixing_increments
from .rows import BladeRow, ExitGeometry, RowPerformance
from .reposition import CoupledRepositioning, elliptic_position_step

Profile = Union[float, Sequence[float]]

#: Loss-scale step of the start-up homotopy (Throughflow.solve): 0, 0.25, 0.5, 0.75, 1 when every
#: step converges; a step that fails is halved, down to HOMOTOPY_MIN_STEP.
HOMOTOPY_STEP = 0.25
HOMOTOPY_MIN_STEP = 1.0 / 64.0


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
    row_iterations: dict = field(default_factory=dict)
    attempts: List[dict] = field(default_factory=list)
    field_change: List[float] = field(default_factory=list)
    blockage_change: List[float] = field(default_factory=list)
    mixing_change: List[float] = field(default_factory=list)
    repositioning: dict = field(default_factory=dict)
    effort: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ThroughflowSolution:
    geometry: SurfaceGeometry
    stations: List[StationFlow]
    rows: List[BladeRow]
    performance: dict
    convergence: Convergence
    blockage: Optional[np.ndarray] = None
    endwall: Optional[EndwallResult] = None
    mixing_coefficient: float = 0.0


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
        mixing: Optional[SpanwiseMixing] = None,
        repositioning: str = "anderson",
        acceleration_depth: int = 40,
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
        self.mixing = mixing
        if repositioning not in ("anderson", "novak"):
            raise ValueError("repositioning must be anderson or novak")
        if not 2 <= acceleration_depth <= 40:
            raise ValueError("acceleration_depth must lie in [2, 40]")
        self.repositioning = repositioning
        self.acceleration_depth = acceleration_depth
        self._kb = self.blockage.copy()  # the blockage factor in use during a solution
        self._loss_scale = 1.0  # below 1 only during the start-up homotopy
        self._effort = dict(outer_iterations=0, station_solves=0, row_model_calls=0, endwall_solves=0)
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
        return self._station_with_context(q,
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

    def _station_with_context(self, q, *args, **kwargs):
        self._effort["station_solves"] += 1
        try:
            return solve_quasi_normal(*args, **kwargs)
        except SolverError as exc:
            exc.diagnostics.setdefault("station", q)
            raise
        except (RuntimeError, ValueError, FloatingPointError) as exc:
            raise SolverError(str(exc), component="quasi_normal", station=q) from exc

    def _inlet_station(self, geo, previous):
        t = geo.y[0] / geo.y[0, -1]
        H = self.gas.enthalpy(_on_span(self.inlet.T0, t))
        s = self.gas.entropy(H, _on_span(self.inlet.P0, t))
        if self.inlet.r_c_theta is not None:
            return self._solve_station(geo, 0, 0.0, H, s, previous, swirl=_on_span(self.inlet.r_c_theta, t))
        alpha = np.radians(_on_span(0.0 if self.inlet.alpha_deg is None else self.inlet.alpha_deg, t))
        return self._solve_station(geo, 0, 0.0, H, s, previous, beta=alpha)

    def _duct_station(self, geo, q, upstream: StationFlow, previous, mix=None):
        # (7-40) to (7-42): r C_theta, H and s carried along each stream surface, plus any mixing change.
        dH, ds, drct = (0.0, 0.0, 0.0) if mix is None else mix
        return self._solve_station(geo, q, 0.0, upstream.H + dH, upstream.s + ds, previous, swirl=upstream.r * upstream.C_theta + drct)

    def _mixing(self, geo, q, upstream: StationFlow, downstream: Optional[StationFlow]):
        """Mixing changes (dH, ds, d rC_theta) over the gap ending at quasi-normal q, or None.

        Trapezoidal along the gap: the rates on the upstream station of this
        pass and on the downstream station of the previous overall iteration
        (Gallimore evaluates the radial derivatives on the previous iteration,
        Part II p. 12), so a row's own loss is mixed across the row.
        """
        mix = self.mixing
        if mix is None or mix.epsilon <= 0.0 or q - 1 < mix.start:
            return None
        dm = geo.m[q] - geo.m[q - 1]
        a = mixing_increments(self.gas, upstream, geo.phi[q - 1], dm, mix.epsilon)
        if downstream is None:
            return a
        b = mixing_increments(self.gas, downstream, geo.phi[q], dm, mix.epsilon)
        return tuple(0.5 * (x + y) for x, y in zip(a, b))

    def _row_station(self, geo, q, row: BladeRow, upstream: StationFlow, previous, tol=1e-12, max_passes=200, relaxation=0.5, mix=None):
        """Exit station of a row, iterating the row model with the exit flow it sets.

        A model whose angle and loss depend on the exit flow (deviation on
        W_m2/W_m1, for example) can overshoot from pass to pass, so after the
        first pass its output is under-relaxed; a model that ignores the exit
        flow converges in two passes as before.

        Mixing across the row (``mix``) adds its heat and shear work to the
        rothalpy, dI = dH - omega d(rC_theta), and its entropy to the exit;
        the exit angle stays the one the row sets, so the blade carries the
        mixing torque (Gallimore lets the angle drift instead, Part II p. 12).
        """
        gas, omega = self.gas, row.omega
        dH, ds_mix, drct = (0.0, 0.0, 0.0) if mix is None else mix
        I = upstream.H - omega * upstream.r * upstream.C_theta + dH - omega * drct  # (7-43)
        H_rel_in = I + 0.5 * (omega * upstream.r) ** 2
        P_rel_in = gas.pressure(H_rel_in, upstream.s)
        H_rel_out = I + 0.5 * (omega * geo.r[q]) ** 2  # (7-47), (7-48)
        P_rel_ideal = gas.pressure(H_rel_out, upstream.s)
        exit_geometry = ExitGeometry(t=geo.y[q] / geo.y[q, -1], y=geo.y[q], r=geo.r[q], z=geo.z[q])
        station = previous
        applied = None
        change = float("inf")
        for iteration in range(1, max_passes + 1):
            self._effort["row_model_calls"] += 1
            try:
                perf: RowPerformance = row.model(upstream, station, exit_geometry)
            except SolverError as exc:
                exc.diagnostics.update(row=row.name, station=q)
                raise
            angle = np.asarray(perf.exit_angle, dtype=float)
            loss = self._loss_scale * np.asarray(perf.loss, dtype=float)
            blocked = None if perf.wake_blockage is None else np.asarray(perf.wake_blockage, dtype=float)
            if not np.all(np.isfinite(angle)) or np.any(np.abs(angle) >= 0.5 * np.pi):
                raise PhysicalStateError("row exit angle is outside the forward-flow range", component="row", row=row.name, station=q)
            if not np.all(np.isfinite(loss)) or np.any(loss < 0.0):
                raise PhysicalStateError("row loss must be finite and nonnegative", component="row", row=row.name, station=q)
            if blocked is not None and (not np.all(np.isfinite(blocked)) or np.any((blocked < 0.0) | (blocked >= 1.0))):
                raise PhysicalStateError("row wake blockage must lie in [0, 1)", component="row", row=row.name, station=q)
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
            s_out = gas.entropy(H_rel_out, P_rel_out) + ds_mix
            wake = None if blocked is None else 1.0 - blocked  # (7-6)
            new = self._solve_station(geo, q, omega, I, s_out, station, beta=angle, wake=wake)
            if station is not None:
                change = max(float(np.max(np.abs(getattr(new, key) - getattr(station, key))) /
                                   max(float(np.max(np.abs(getattr(new, key)))), 1.0))
                             for key in ("Wm", "C_theta", "H", "P"))
                change = max(change, float(np.max(np.abs(new.s - station.s))) / gas.cp)
                if change <= tol:
                    self._row_convergence[row.name] = dict(iterations=iteration, residual=change, tolerance=tol)
                    return new, perf
            station = new
        raise SolverError("row {} did not converge with its exit flow".format(row.name), component="row",
                          row=row.name, station=q, iterations=max_passes, residual=change)

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
    def solve(self, tol: float = 1e-9, max_iterations: int = 500, b_star: float = 4.0, start=None) -> ThroughflowSolution:
        """Solve from uniform-flow stream surfaces; if that fails, through a loss homotopy.

        A cold start can fail where a solution exists: on the first outer
        iterations the stream surfaces are far from their final positions, a
        row whose loss rises with its exit diffusion then sees a low exit
        velocity, its loss grows, the velocity falls further and the
        quasi-normal has no solution. The fallback solves again with the row
        losses scaled from 0 up to 1 in steps of HOMOTOPY_STEP, starting every
        step from the stream surfaces of the last converged one; a step that
        fails is halved and retried, down to HOMOTOPY_MIN_STEP, and a converged
        step lets the next one grow back. The last step is the full model, so
        its solution is the model's solution at this point. A point that
        converges from the cold start never reaches the fallback, and when the
        fallback fails too the cold-start outcome is returned.
        """
        self._effort = dict(outer_iterations=0, station_solves=0, row_model_calls=0, endwall_solves=0)
        from .limits import enforce_inlet_capacity
        enforce_inlet_capacity(self)
        if start is not None:
            start = np.asarray(start, dtype=float)
            if (start.shape != (self.qn.count, self.n) or not np.all(np.isfinite(start))
                    or np.any(np.diff(start, axis=1) <= 0.0)
                    or np.any(start[:, 0] != 0.0) or np.any(start[:, -1] != 1.0)):
                raise SolverError("inadmissible restart stream-surface positions", kind="invalid_restart", component="initialization")
        attempts = []

        def attempt(scale, start=None, initialization="cold"):
            methods = ("anderson", "novak") if self.repositioning == "anderson" and self.curvature == "full" else ("novak",)
            last_result = last_error = None
            for method in methods:
                before = dict(self._effort)
                try:
                    result = self._solve(tol, max_iterations, b_star, start, method)
                except (RuntimeError, ValueError, FloatingPointError) as exc:
                    attempts.append(dict(loss_scale=scale, method=method, initialization=initialization, converged=False,
                                         effort={k: self._effort[k] - before[k] for k in before},
                                         failure=dict(getattr(exc, "diagnostics", {"message": str(exc), "kind": "numerical_failure"}))))
                    last_error = exc
                    continue
                attempts.append(dict(loss_scale=scale, method=method, initialization=initialization,
                                     converged=result.convergence.converged, iterations=result.convergence.iterations,
                                     repositioning=result.convergence.repositioning,
                                     position_residual=result.convergence.position_change[-1] if np.isfinite(result.convergence.position_change[-1]) else None,
                                     field_residual=result.convergence.velocity_change[-1] if np.isfinite(result.convergence.velocity_change[-1]) else None,
                                     effort={k: self._effort[k] - before[k] for k in before}))
                result.convergence.attempts = list(attempts)
                result.convergence.effort = dict(self._effort)
                last_result = result
                if result.convergence.converged:
                    return result
            if last_result is not None:
                last_result.convergence.attempts = list(attempts)
                last_result.convergence.effort = dict(self._effort)
                return last_result
            if isinstance(last_error, SolverError):
                last_error.diagnostics["attempts"] = list(attempts)
                last_error.diagnostics["effort"] = dict(self._effort)
            raise last_error

        if start is not None:
            try:
                warm = attempt(1.0, start, "restart")
                if warm.convergence.converged:
                    return warm
            except (RuntimeError, ValueError, FloatingPointError):
                pass
        try:
            cold = attempt(1.0)
        except (RuntimeError, ValueError, FloatingPointError) as exc:  # ChokedError is a RuntimeError
            cold, error = None, exc
        if cold is not None and cold.convergence.converged:
            return cold
        t_start, done, step = None, None, HOMOTOPY_STEP
        try:
            while done is None or done < 1.0:
                scale = 0.0 if done is None else min(1.0, done + step)
                self._loss_scale = scale
                try:
                    sol = attempt(scale, t_start, "homotopy")
                    converged = sol.convergence.converged
                except (RuntimeError, ValueError, FloatingPointError):
                    converged = False
                if converged:
                    done = scale
                    t_start = sol.geometry.y / sol.geometry.y[:, -1:]
                    step = min(HOMOTOPY_STEP, 2.0 * step)
                elif done is None or step <= HOMOTOPY_MIN_STEP:
                    break
                else:
                    step *= 0.5
            else:
                return sol
        finally:
            self._loss_scale = 1.0
        if cold is None:
            if isinstance(error, SolverError):
                error.diagnostics["attempts"] = list(attempts)
                error.diagnostics["effort"] = dict(self._effort)
            raise error
        cold.convergence.attempts = list(attempts)
        cold.convergence.effort = dict(self._effort)
        return cold

    def _coupled_iteration(self, t, previous, performance, row_tol):
        """Evaluate one complete coupled map; the caller owns rollback."""
        geo = surface_geometry(self.qn, t, self.curvature, self.annulus)
        stations, performance = list(previous), dict(performance)
        kb_start = self._kb.copy()
        if self.mixing is not None and previous[0] is not None:
            eps_old = self.mixing.epsilon
            eps_new = self.mixing.update(self.gas, previous)
        for q in range(self.qn.count):
            if q == 0:
                stations[q] = self._inlet_station(geo, previous[q])
                continue
            mix = self._mixing(geo, q, stations[q-1], previous[q])
            if (q-1) in self.row_at:
                row = self.row_at[q-1]
                stations[q], performance[row.name] = self._row_station(
                    geo, q, row, stations[q-1], previous[q], tol=row_tol, mix=mix)
            else:
                stations[q] = self._duct_station(geo, q, stations[q-1], previous[q], mix=mix)
        target = self._mass_fraction_positions(geo, stations, np.linspace(0., 1., self.n))
        move = float(np.max(np.abs(target-t)))
        field = np.inf if previous[0] is None else max(
            max(float(np.max(np.abs(getattr(a, key)-getattr(b, key)))) /
                max(float(np.max(np.abs(getattr(a, key)))), 1.) for key in ('Wm', 'C_theta', 'H', 'P'))
            for a, b in zip(stations, previous))
        if previous[0] is not None:
            field = max(field, max(float(np.max(np.abs(a.s-b.s)))/self.gas.cp for a, b in zip(stations, previous)))
        blockage_change = mixing_change = 0.
        endwall_result = None
        if self.endwall is not None:
            self._effort['endwall_solves'] += 1
            endwall_result = self.endwall.solve(self, geo, stations, performance)
            kb_target = 1.-np.clip(endwall_result.blockage, 0., self.max_blockage)
            blockage_change = float(np.max(np.abs(kb_target-self._kb)))
            self._kb += self.endwall_relaxation*(kb_target-self._kb)
        if self.mixing is not None and previous[0] is not None:
            mixing_change = abs(eps_new-eps_old)/max(abs(eps_new), 1e-30)
        return (geo, stations, performance, endwall_result, kb_start, target, move,
                field, blockage_change, mixing_change)

    def _solve(self, tol, max_iterations, b_star, t_start=None, method="novak") -> ThroughflowSolution:
        t = uniform_flow_fractions(self.qn, np.linspace(0., 1., self.n)) if t_start is None else np.array(t_start, dtype=float)
        stations = [None]*self.qn.count
        performance, self._row_convergence = {}, {}
        conv = Convergence()
        accelerator = CoupledRepositioning(self.acceleration_depth) if method == 'anderson' else None
        last_move, row_tol = np.inf, 1e-6
        self._kb = self.blockage.copy()
        endwall_result = None
        if self.endwall is not None:
            self.endwall.reset()
        if self.mixing is not None:
            self.mixing.epsilon = 0.
        checkpoint, accelerated_trial = None, False
        retries, backtracked, residual_history = 0, [], []
        def repositioning_diagnostics():
            return dict(method=method, depth=self.acceleration_depth if accelerator else 0,
                preconditioner='elliptic_half_step' if accelerator else 'novak_diagonal',
                accepted_steps=0 if accelerator is None else accelerator.accepted,
                rejected_steps=0 if accelerator is None else accelerator.rejected,
                backtracked_evaluations=len(backtracked), rejected_evaluations=list(backtracked))
        for iteration in range(1, max_iterations+1):
            self._effort['outer_iterations'] += 1
            try:
                evaluated = self._coupled_iteration(t, stations, performance, row_tol)
                residual = max(evaluated[6], evaluated[8], evaluated[9])
                if accelerated_trial and residual_history and residual > 2*max(residual_history[-5:]):
                    raise SolverError('accelerated coupled residual grew beyond the safeguard',
                                      component='repositioning', residual=residual)
            except (RuntimeError, ValueError, FloatingPointError) as exc:
                if accelerator is None or checkpoint is None or retries >= 8:
                    if not isinstance(exc, SolverError):
                        exc = SolverError(str(exc), component='outer')
                    exc.diagnostics.update(repositioning=repositioning_diagnostics(), outer_evaluation=iteration)
                    raise exc
                # Retry a smaller ordinary step from the last complete state.
                # Rejected evaluations still consume the outer iteration budget.
                base_t, base_kb, safe_t, safe_kb, stations, performance, wall_state, mixing, row_state = checkpoint
                alpha = .5**retries
                t = base_t+alpha*(safe_t-base_t)
                self._kb = base_kb+alpha*(safe_kb-base_kb)
                if self.endwall is not None:
                    self.endwall._delta_nu = dict(wall_state)
                if self.mixing is not None:
                    self.mixing.epsilon = mixing
                self._row_convergence = dict(row_state)
                for row in self.rows:
                    if hasattr(row.model, '_cached'):
                        row.model._cached = None
                accelerator.history.clear()
                accelerator.rejected += 1
                retries += 1
                accelerated_trial = False
                backtracked.append(dict(iteration=iteration, fraction=alpha,
                    failure=dict(getattr(exc, 'diagnostics', {'kind': 'numerical_failure', 'message': str(exc)}))))
                continue
            geo, stations, performance, endwall_result, kb_start, target, move, field, blockage_change, mixing_change = evaluated
            retries = 0
            residual_history.append(residual)
            if accelerator is None and move > last_move:
                b_star = .5*(b_star+1.)
            last_move = move
            dv = max(field, blockage_change, mixing_change)
            conv.field_change.append(field)
            conv.blockage_change.append(blockage_change)
            conv.mixing_change.append(mixing_change)
            conv.row_iterations = dict(self._row_convergence)
            conv.iterations = iteration
            conv.position_change.append(move)
            conv.velocity_change.append(dv)
            if move <= tol and dv <= tol:
                conv.converged = True
                break
            row_tol = float(np.clip(.01*min(move, dv), 1e-12, 1e-6))
            try:
                damping = self._damping(geo, stations, b_star)
                correction = (damping*(target-t) if accelerator is None else
                              .5*elliptic_position_step(geo, stations, target-t))
                safe_t = t+correction
                checkpoint = (t.copy(), kb_start.copy(), safe_t.copy(), self._kb.copy(), list(stations),
                    dict(performance), {} if self.endwall is None else dict(self.endwall._delta_nu),
                    0. if self.mixing is None else self.mixing.epsilon, dict(self._row_convergence))
                if accelerator is None:
                    t = safe_t
                else:
                    accepted = accelerator.accepted
                    t, self._kb = accelerator.step(t, target, damping, kb_start, self._kb,
                        self.endwall_relaxation, min(float(np.min(self.blockage)), 1.-self.max_blockage),
                        position_step=correction)
                    accelerated_trial = accelerator.accepted > accepted
            except (RuntimeError, ValueError, FloatingPointError) as exc:
                if not isinstance(exc, SolverError):
                    exc = SolverError(str(exc), component='repositioning')
                exc.diagnostics.update(repositioning=repositioning_diagnostics(), outer_evaluation=iteration)
                raise exc
        conv.iterations = iteration
        conv.repositioning = repositioning_diagnostics()
        return ThroughflowSolution(geometry=geo, stations=stations, rows=self.rows, performance=performance, convergence=conv,
            blockage=self._kb.copy(), endwall=endwall_result,
            mixing_coefficient=0. if self.mixing is None else self.mixing.epsilon)
