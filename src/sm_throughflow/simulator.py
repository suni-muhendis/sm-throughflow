"""The simulator: axial compressors on the streamline-curvature solver with Aungier's models."""
import math
from typing import Any, Dict, List, Tuple

import numpy as np
from sm_core import BaseSimulator

from .geometry import blade_sections, station_grid
from .provenance import evaluation_identity
from .outcomes import failure_evidence
from .contracts import AUNGIER_PROFILES, SIMULATOR_VERSION, SPAN_FRACTIONS, ThroughflowDesignV2, ThroughflowTaskV2


def _finite_list(values) -> List[Any]:
    return [float(v) if math.isfinite(v) else None for v in np.asarray(values, dtype=float).ravel()]


class SlcAungierSimulator(BaseSimulator):
    """Solves every operating point of a task with ``sm_throughflow.solver``.

    Quasi-normals include every nonredundant passage vertex and row edge.
    Each row occupies one gap; other gaps are independently refinable ducts.
    """

    VERSION = SIMULATOR_VERSION
    #: Experimental switch, off in every released profile: None, or "gallimore" for spanwise mixing
    #: (sm_throughflow.solver.mixing) at the level of Gallimore and Cumpsty's eq. (9).
    mixing_model = None

    def simulate(self, inputs: Dict[str, Any]) -> Tuple[bool, Dict[str, float], Dict[str, Any], str]:
        try:
            design = ThroughflowDesignV2.model_validate(inputs["design"])
            task = ThroughflowTaskV2.model_validate(inputs["task"])
            task.validate_design_ownership(design)
        except Exception as exc:
            return False, {}, {"failure": {"kind": "invalid_input", "classification": "invalid_input",
                                          "physical_limit_established": False, "message": str(exc)}}, "invalid simulation inputs: {}".format(exc)
        provenance = evaluation_identity(design, task, AUNGIER_PROFILES[task.physics.physics_profile], self.mixing_model)
        metrics: Dict[str, float] = {}
        points = []
        failures = []
        for index, point in enumerate(task.operating_points):
            try:
                point_metrics, point_raw = self._solve_point(design, task, point)
            except Exception as exc:
                failure = dict(failure_evidence(exc), operating_point=point.name)
                failures.append(failure)
                points.append(dict(name=point.name, converged=False, failure=failure))
                continue
            prefix = "" if index == 0 else point.name + "."
            metrics.update({prefix + key: value for key, value in point_metrics.items()})
            point_raw["metrics"] = point_metrics
            points.append(point_raw)
        raw = {
            "simulator_version": self.VERSION,
            "provenance": provenance,
            "physics_profile": dict(profile_id=task.physics.physics_profile, **AUNGIER_PROFILES[task.physics.physics_profile]),
            "operating_points": points,
            "span_fractions": list(SPAN_FRACTIONS),
        }
        if failures:
            raw.update(failure=failures[0], failures=failures)
            return False, metrics, raw, "; ".join("operating point {!r} failed: {}".format(f["operating_point"], f["message"]) for f in failures)
        return True, metrics, raw, ""

    # ------------------------------------------------------------ build
    @staticmethod
    def _sections(row, stations):
        """Camber, stagger, solidity, chi1/camber and a/c of the row's eleven design sections, and the shape
        keywords of ``blade_geometry.section``; each section sits at its span fraction on the mid-chord plane."""
        return blade_sections(row, stations)

    @staticmethod
    def section_shape(row, stations):
        """chi1/camber and a/c at the eleven sections, for a multiple-circular-arc row; None otherwise."""
        if row.camberline != "multiple_circular_arc":
            return None
        sections = SlcAungierSimulator._sections(row, stations)
        return {"chi1_over_camber": [s["chi1_over_camber"] for s in sections], "a_c": [s["a_c"] for s in sections]}

    @staticmethod
    def throat_over_pitch(row, stations) -> List[float]:
        """o/s of the constructed cascade at the row's eleven sections (Aungier section 4.9).

        Each section sits at its span fraction on the row's mid-chord plane,
        with pitch 2 pi r / Z; computed once per row, as Aungier does.
        """
        from .correlations.blade_geometry import throat_opening_ratio_geometric

        return [throat_opening_ratio_geometric(row.profile, row.camberline, s["camber"], s["stagger"], s["t_c"], s["solidity"],
                                               row.max_camber_location, row.edge_radius_to_chord, **s["shape"])
                for s in SlcAungierSimulator._sections(row, stations)]

    @staticmethod
    def expansion_angles(row, stations):
        """Suction-surface expansion angle of the shock model at the row's eleven sections, degrees.

        Read off the constructed cascade for double-circular-arc blades, whose
        meanline may be any of the contract's camberlines (Aungier's (6-65) to
        (6-69) assume a circular arc); None for the NACA 65 and C.4 profiles,
        which keep the book's relation. The sections are those of
        ``throat_over_pitch``.
        """
        if row.profile not in ("dca", "mca"):
            return None
        from .correlations.blade_geometry import suction_surface_expansion_geometric

        return [suction_surface_expansion_geometric(row.profile, row.camberline, s["camber"], s["stagger"], s["t_c"], s["solidity"],
                                                    row.max_camber_location, row.edge_radius_to_chord, **s["shape"])
                for s in SlcAungierSimulator._sections(row, stations)]

    @staticmethod
    def shock_surface_angles(row, stations):
        """Cylindrical surfaces and legacy tangents for the passage-shock approximation.

        Common arc-length samples permit span interpolation of the surface;
        the row model finds the foot after projection on the current cone.
        """
        if row.profile not in ("dca", "mca"):
            return None
        from .correlations.blade_geometry import suction_surface_shock_angles, section, _stagger, _arc_length

        angles = [suction_surface_shock_angles(row.profile, row.camberline, s["camber"], s["stagger"],
                    s["t_c"], s["solidity"], row.max_camber_location, row.edge_radius_to_chord, **s["shape"])
                  for s in SlcAungierSimulator._sections(row, stations)]
        surfaces = []
        for s in SlcAungierSimulator._sections(row, stations):
            upper, _, _ = section(row.profile, row.camberline, s['camber'], s['t_c'],
                row.max_camber_location, row.edge_radius_to_chord, **s['shape'])
            p = _stagger(upper, s['stagger'])*s['solidity']
            arc = _arc_length(p[:, 0], p[:, 1])
            surfaces.append(np.column_stack([np.interp(np.linspace(0., 1., 401), arc, p[:, k]) for k in (0, 1)]).tolist())
        return dict(leading=[a[0] for a in angles], foot=[a[1] for a in angles], surfaces=surfaces)

    @staticmethod
    def build(design: ThroughflowDesignV2, task: ThroughflowTaskV2, point):
        """The solver problem of one operating point: (Throughflow, row models by row_id)."""
        from .solver import Annulus, InletCondition, PerfectGas, QuasiNormals, Throughflow
        from .solver.aungier_row import AungierCompressorRow, BladeSections, ShroudSeal, TipClearance
        from .solver.endwall import EndwallBoundaryLayers, sutherland_air

        profile = AUNGIER_PROFILES[task.physics.physics_profile]
        gas = PerfectGas(cp=task.gas.cp_j_kg_k, R=task.gas.gas_constant_j_kg_k)
        stations, z, row_indices = station_grid(design, task.numerics.duct_subdivisions)
        annulus = Annulus.from_points([(s.axial_m, s.hub_radius_m) for s in stations], [(s.axial_m, s.shroud_radius_m) for s in stations])
        qn = QuasiNormals.on(annulus, z)
        omega = point.shaft_speed_rpm * 2.0 * math.pi / 60.0
        guide_vanes = set(design.inlet_guide_vanes())
        span = np.asarray(SPAN_FRACTIONS, dtype=float)
        models, rows = {}, []
        for k, row in enumerate(design.rows):
            sections = BladeSections(span, row.metal_angle_in_deg, row.metal_angle_out_deg, row.chord_m, row.thickness_to_chord, coordinate="span")
            clearance = seal = None
            if row.row_type == "rotor":
                clearance = TipClearance(row.tip_clearance_m, "shroud")
            elif row.hub_clearance_m is not None:
                clearance = TipClearance(row.hub_clearance_m, "hub")
            else:
                x = row.leading_edge_axial_m
                r_seal = float(annulus.hub_radius(x))
                s = row.shroud_seal
                seal = ShroudSeal(r_seal, s.clearance_m, s.fin_count, s.fin_pitch_m, s.fin_thickness_m, "hub")
            model = AungierCompressorRow(
                sections, row.blade_count, omega if row.row_type == "rotor" else 0.0, gas,
                profile=row.profile, camberline=row.camberline, a_c=row.max_camber_location, row_number=k + 1,
                inlet_guide_vane=row.row_id in guide_vanes, clearance=clearance, seal=seal,
                throat_over_pitch=SlcAungierSimulator.throat_over_pitch(row, stations),
                expansion_angle=SlcAungierSimulator.expansion_angles(row, stations),
                shock_surface_angles=SlcAungierSimulator.shock_surface_angles(row, stations),
                section_shape=SlcAungierSimulator.section_shape(row, stations),
                viscosity=sutherland_air, K1=profile["K1"], max_loss=profile["max_loss"], smoothing=profile["smoothing"], shock_mean=profile["shock_mean"],
            )
            models[row.row_id] = model
            rows.append(model.blade_row(row.row_id, row_indices[row.row_id]))
        endwall = EndwallBoundaryLayers(inlet_blockage=task.physics.inlet_blockage,
                                        max_passes=task.numerics.endwall_max_iterations,
                                        subdivisions=task.numerics.endwall_subdivisions) if profile["endwall"] else None
        inlet = InletCondition(P0=task.inlet.total_pressure_pa, T0=task.inlet.total_temperature_k, alpha_deg=task.inlet.flow_angle_deg)
        mixing = SlcAungierSimulator.spanwise_mixing(design, annulus, omega, row_indices) if SlcAungierSimulator.mixing_model == "gallimore" else None
        flow = Throughflow(annulus, qn, inlet, point.mass_flow_kg_s, rows=rows, gas=gas, stream_surfaces=task.numerics.stream_surfaces,
                           curvature=task.numerics.curvature, endwall=endwall, mixing=mixing,
                           repositioning=task.numerics.repositioning, acceleration_depth=task.numerics.acceleration_depth)
        return flow, models

    @staticmethod
    def spanwise_mixing(design, annulus, omega, row_indices=None):
        """Gallimore's uniform mixing over the bladed region (sm_throughflow.solver.mixing).

        The paper defines its inputs for a repeating stage; here L_s is the
        bladed axial length per rotor, t the mean midspan maximum thickness of
        all rows and U_m the mean midspan blade speed of the rotors.
        """
        from .solver.mixing import SpanwiseMixing

        rows = design.rows
        row_indices = station_grid(design)[2] if row_indices is None else row_indices
        mid = len(SPAN_FRACTIONS) // 2
        rotors = [row for row in rows if row.row_type == "rotor"]
        stages = max(1, len(rotors))
        length = (rows[-1].trailing_edge_axial_m - rows[0].leading_edge_axial_m) / stages
        thickness = float(np.mean([row.chord_m[mid] * row.thickness_to_chord[mid] for row in rows]))
        speeds = []
        for row in rotors:
            x = 0.5 * (row.leading_edge_axial_m + row.trailing_edge_axial_m)
            speeds.append(omega * 0.5 * (float(annulus.hub_radius(x)) + float(annulus.shroud_radius(x))))
        return SpanwiseMixing(stage_length=length, thickness=thickness, blade_speed=float(np.mean(speeds)) if speeds else 1.0,
                              start=row_indices[rows[0].row_id], stage_in=row_indices[rows[0].row_id],
                              stage_out=row_indices[rows[-1].row_id] + 1, stages=stages)

    # ------------------------------------------------------------ solve
    @classmethod
    def _solve_with_grid_continuation(cls, design, task, point, flow, start):
        """Retry failed fine-grid initialization using checked coarser solutions.

        Each level keeps the task's full physics, tolerance and per-attempt
        budget. Only stream positions are interpolated; all fields, blockage
        and wall corrections are solved again. Every attempted grid and its
        work remain in the final success or failure telemetry.
        """
        from .solver.errors import SolverError
        from .solver.verification import verify_solution

        attempts, effort = [], dict.fromkeys(flow._effort, 0)

        def run(candidate, positions, subdivisions, role):
            solution = None
            try:
                solution = candidate.solve(tol=task.numerics.tolerance,
                    max_iterations=task.numerics.max_iterations, b_star=4., start=positions)
                if not solution.convergence.converged:
                    raise SolverError('throughflow grid attempt did not converge', component='outer',
                        iterations=solution.convergence.iterations,
                        residual=max(solution.convergence.position_change[-1], solution.convergence.velocity_change[-1]),
                        attempts=solution.convergence.attempts, effort=solution.convergence.effort,
                        details=dict(repositioning=solution.convergence.repositioning))
                verify_solution(candidate, solution, task.numerics.tolerance)
                lo, hi = AUNGIER_PROFILES[task.physics.physics_profile]['temperature_bounds_k']
                if (min(float(np.min(st.T)) for st in solution.stations) < lo or
                        max(float(np.max(st.T0)) for st in solution.stations) > hi):
                    raise SolverError('grid seed temperature outside model scope', kind='outside_model_scope',
                        component='gas', attempts=solution.convergence.attempts, effort=solution.convergence.effort)
            except (RuntimeError, ValueError, FloatingPointError) as exc:
                if not isinstance(exc, SolverError):
                    exc = SolverError(str(exc), component='outer')
                records = exc.diagnostics.get('attempts', [] if solution is None else solution.convergence.attempts)
                attempts.extend(dict(a, duct_subdivisions=subdivisions, grid_role=role) for a in records)
                if not records:
                    attempts.append(dict(converged=False, duct_subdivisions=subdivisions, grid_role=role,
                                         failure=dict(exc.diagnostics), effort=dict(candidate._effort)))
                for key, value in candidate._effort.items():
                    effort[key] += value
                raise exc
            attempts.extend(dict(a, duct_subdivisions=subdivisions, grid_role=role)
                            for a in solution.convergence.attempts)
            for key, value in candidate._effort.items():
                effort[key] += value
            return solution

        requested = task.numerics.duct_subdivisions
        try:
            solution = run(flow, start, requested, 'requested_initial')
        except SolverError as initial_error:
            if requested <= 1 or task.numerics.curvature != 'full' or initial_error.diagnostics['kind'] not in (
                    'numerical_failure', 'quasi_normal_capacity'):
                initial_error.diagnostics.update(attempts=attempts, effort=effort)
                raise
            levels, level = [], 1
            while level < requested:
                levels.append(level)
                level *= 2
            seed = None
            try:
                for level in levels + [requested]:
                    candidate = flow
                    if level != requested:
                        level_task = task.model_copy(deep=True)
                        level_task.numerics.duct_subdivisions = level
                        candidate, _ = cls.build(design, level_task, point)
                    positions = None if seed is None else np.column_stack([
                        np.interp(candidate.qn.z_hub, seed.geometry.z[:, k],
                                  seed.geometry.y[:, k]/seed.geometry.y[:, -1])
                        for k in range(candidate.n)])
                    solution = run(candidate, positions, level,
                                   'requested_retry' if level == requested else 'coarse_seed')
                    seed = solution
            except (RuntimeError, ValueError, FloatingPointError) as exc:
                if not isinstance(exc, SolverError):
                    exc = SolverError(str(exc), component='initialization')
                initial_error.diagnostics.update(attempts=list(attempts), effort=dict(effort),
                    grid_continuation_failure={k:v for k,v in exc.diagnostics.items() if k not in ('attempts','effort')})
                raise initial_error
        solution.convergence.attempts = attempts
        solution.convergence.effort = effort
        return solution

    @classmethod
    def solve_state(cls, design, task, point, restart=None):
        """Checked full-model solve shared by environment and map/research adapters."""
        from .solver.errors import SolverError
        from .solver.verification import verify_solution
        from .provenance import digest

        lo, hi = AUNGIER_PROFILES[task.physics.physics_profile]["temperature_bounds_k"]
        if not lo <= task.inlet.total_temperature_k <= hi:
            raise SolverError("inlet temperature outside the experimental constant-cp air envelope [{}, {}] K".format(lo, hi),
                              kind="outside_model_scope", component="gas",
                              details={"inlet_total_temperature_k": task.inlet.total_temperature_k})
        try:
            flow, models = cls.build(design, task, point)
        except ValueError as exc:
            raise SolverError(str(exc), kind="outside_model_scope", component="geometry") from exc
        key = digest(dict(design=design.model_dump(mode="json"),
                          task=task.model_dump(mode="json", exclude={"operating_points"}),
                          rpm=point.shaft_speed_rpm, mixing_model=cls.mixing_model))
        if restart is not None and restart.get("key") != key:
            raise SolverError("restart belongs to a different geometry, speed or configuration",
                              kind="invalid_restart", component="initialization")
        # Direct three-point curvature resolves modes hidden by the old stencil.
        # B*=4 contracts the high-frequency near-planar mode (B < pi**2/2);
        # it is a versioned numerical choice, not a fitted physical coefficient.
        sol = cls._solve_with_grid_continuation(design, task, point, flow,
                                               None if restart is None else restart['positions'])
        if not sol.convergence.converged:
            raise SolverError("the throughflow solution did not converge in {} iterations (last changes {:.3e}, {:.3e})".format(
                sol.convergence.iterations, sol.convergence.position_change[-1], sol.convergence.velocity_change[-1]), component="outer",
                              iterations=sol.convergence.iterations,
                              residual=max(sol.convergence.position_change[-1], sol.convergence.velocity_change[-1]),
                              details={"attempts": sol.convergence.attempts,
                                       "repositioning": sol.convergence.repositioning},
                              attempts=sol.convergence.attempts, effort=sol.convergence.effort)
        try:
            balances = verify_solution(flow, sol, task.numerics.tolerance)
        except SolverError as exc:
            exc.diagnostics.update(attempts=sol.convergence.attempts, effort=sol.convergence.effort)
            raise
        temperature_min = min(float(np.min(st.T)) for st in sol.stations)
        temperature_max = max(float(np.max(st.T0)) for st in sol.stations)
        lo, hi = AUNGIER_PROFILES[task.physics.physics_profile]["temperature_bounds_k"]
        if temperature_min < lo or temperature_max > hi:
            raise SolverError("temperature outside the experimental constant-cp air envelope [{}, {}] K".format(lo, hi),
                              kind="outside_model_scope", component="gas", details={"static_min_k": temperature_min, "total_max_k": temperature_max},
                              attempts=sol.convergence.attempts, effort=sol.convergence.effort)
        restart = dict(key=key, mass_flow=point.mass_flow_kg_s,
                       positions=(sol.geometry.y / sol.geometry.y[:, -1:]).tolist())
        return flow, models, sol, balances, restart

    def _solve_point(self, design, task, point, restart=None, return_restart=False):
        from .solver import averaged_total_state, polytropic_efficiency
        from .solver.limits import inlet_capacity, solution_limits
        flow, models, sol, balances, restart = self.solve_state(design, task, point, restart)
        gas = flow.gas
        temperature_min = min(float(np.min(st.T)) for st in sol.stations)
        temperature_max = max(float(np.max(st.T0)) for st in sol.stations)
        first, last = sol.stations[0], sol.stations[-1]
        T1, P1 = averaged_total_state(gas, first)
        T2, P2 = averaged_total_state(gas, last)
        pr, tr = P2 / P1, T2 / T1
        k = (gas.gamma - 1.0) / gas.gamma
        row_data, extremes = [], dict(loss=0.0, D_eq=0.0, mach=0.0, margin=np.inf)
        for row in design.rows:
            d = sol.performance[row.row_id].diagnostics
            margin = d.get("equivalent_velocity_ratio", np.nan) / d.get("stall_velocity_ratio", np.nan) - 1.0 if "equivalent_velocity_ratio" in d else np.nan
            extremes["loss"] = max(extremes["loss"], float(np.max(d["loss"])))
            extremes["D_eq"] = max(extremes["D_eq"], float(np.max(d["equivalent_diffusion"])))
            extremes["mach"] = max(extremes["mach"], float(np.max(d["relative_inlet_mach"])))
            extremes["margin"] = min(extremes["margin"], float(np.nanmin(margin)))
            entry = {"row_id": row.row_id, "row_type": row.row_type, "stall_margin": _finite_list(margin)}
            entry.update({key: _finite_list(value) for key, value in d.items() if np.ndim(value) > 0})
            entry["seal_leakage_mass_flow"] = float(d.get("seal_leakage_mass_flow", 0.0))
            entry["section_throat_over_pitch"] = _finite_list(models[row.row_id].throat_over_pitch)
            row_data.append(entry)
        stage_data = []
        index = {row.name: row.inlet for row in sol.rows}
        for stage_id in dict.fromkeys(r.stage_id for r in design.rows if r.stage_id is not None):
            members = [index[r.row_id] for r in design.rows if r.stage_id == stage_id]
            a, b = sol.stations[min(members)], sol.stations[max(members) + 1]
            Ta, Pa = averaged_total_state(gas, a)
            Tb, Pb = averaged_total_state(gas, b)
            stage_data.append({"stage_id": stage_id, "pressure_ratio_total": Pb / Pa, "temperature_ratio_total": Tb / Ta,
                               "efficiency_polytropic": polytropic_efficiency(gas, a, b)})
        metrics = {
            "pressure_ratio_total": pr,
            "temperature_ratio_total": tr,
            "efficiency_polytropic": polytropic_efficiency(gas, first, last),
            "efficiency_isentropic": (pr ** k - 1.0) / (tr - 1.0),
            "power_W": point.mass_flow_kg_s * gas.cp * (T2 - T1),
            "mass_flow_kg_s": point.mass_flow_kg_s,
            "shaft_speed_rpm": point.shaft_speed_rpm,
            "stage_count": float(design.stage_count),
            "stream_surface_count": float(flow.n),
            "exit_blockage": float(1.0 - sol.blockage[-1]),
            "max_blockage": float(np.max(1.0 - sol.blockage)),
            "max_loss_coefficient": extremes["loss"],
            "max_equivalent_diffusion": extremes["D_eq"],
            "max_relative_inlet_mach": extremes["mach"],
            "min_stall_margin": extremes["margin"],
            "solver_iterations": float(sol.convergence.iterations),
        }
        if not all(math.isfinite(v) for v in metrics.values()):
            raise ValueError("non-finite summary metrics: {}".format(sorted(key for key, v in metrics.items() if not math.isfinite(v))))
        raw = {
            "name": point.name,
            "converged": True,
            "limits": dict(solution_limits(sol), inlet_capacity=inlet_capacity(flow)),
            "rows": row_data,
            "stages": stage_data,
            "blockage": _finite_list(1.0 - sol.blockage),
            "station_axial_m": _finite_list(flow.qn.z_hub),
            "row_station_indices": {r.name: {"inlet": r.inlet, "exit": r.inlet + 1} for r in sol.rows},
            "exit_span": {
                "span_fraction": _finite_list(last.t),
                "total_pressure_pa": _finite_list(last.P0),
                "total_temperature_k": _finite_list(last.T0),
                "flow_angle_deg": _finite_list(np.degrees(last.alpha)),
                "meridional_velocity_m_s": _finite_list(last.Wm),
            },
            "verification": balances,
            "validity": {"empirical_validation": "pending", "score_eligible": False,
                         "reynolds_min": min(float(np.min(sol.performance[r.row_id].diagnostics["reynolds_number"])) for r in design.rows),
                         "reynolds_max": max(float(np.max(sol.performance[r.row_id].diagnostics["reynolds_number"])) for r in design.rows),
                         "relative_inlet_mach_max": extremes["mach"],
                         "mach_reynolds_validated_range": None,
                         "temperature_static_min_k": temperature_min, "temperature_total_max_k": temperature_max,
                         "loss_limit_rows": [r.row_id for r in design.rows if np.any(sol.performance[r.row_id].diagnostics["loss_limit_active"])],
                         "blockage_limit_stations": ([] if sol.endwall is None else
                             np.flatnonzero((sol.endwall.blockage < 0.0) | (sol.endwall.blockage > flow.max_blockage)).tolist()),
                         "meridional_mach_limit_stations": [q for q, st in enumerate(sol.stations)
                             if st.solver_diagnostics.get("meridional_mach_limit_active")]},
            "convergence": {"rows": sol.convergence.row_iterations, "attempts": sol.convergence.attempts,
                            "effort": sol.convergence.effort,
                            "repositioning": sol.convergence.repositioning,
                            "tolerance": task.numerics.tolerance,
                            "field_change": sol.convergence.field_change[-1],
                            "blockage_change": sol.convergence.blockage_change[-1],
                            "mixing_change": sol.convergence.mixing_change[-1],
                            "quasi_normals": [st.solver_diagnostics for st in sol.stations],
                            "endwalls": [] if sol.endwall is None else sol.endwall.convergence,
                            "iterations": sol.convergence.iterations, "position_change": sol.convergence.position_change[-1],
                            "velocity_change": sol.convergence.velocity_change[-1]},
        }
        return (metrics, raw, restart) if return_restart else (metrics, raw)
