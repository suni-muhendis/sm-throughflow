"""The simulator: axial compressors on the streamline-curvature solver with Aungier's models."""
import math
from typing import Any, Dict, List, Tuple

import numpy as np
from sm_core import BaseSimulator

from .contracts import AUNGIER_PROFILES, SIMULATOR_VERSION, SPAN_FRACTIONS, ThroughflowDesignV2, ThroughflowTaskV2


def _finite_list(values) -> List[Any]:
    return [float(v) if math.isfinite(v) else None for v in np.asarray(values, dtype=float).ravel()]


class SlcAungierSimulator(BaseSimulator):
    """Solves every operating point of a task with ``sm_throughflow.solver``.

    Quasi-normals sit at the passage inlet, at every row's leading and
    trailing edge and at the passage outlet; each row occupies the gap between
    its two edges and every other gap is a duct.
    """

    VERSION = SIMULATOR_VERSION

    def simulate(self, inputs: Dict[str, Any]) -> Tuple[bool, Dict[str, float], Dict[str, Any], str]:
        try:
            design = ThroughflowDesignV2.model_validate(inputs["design"])
            task = ThroughflowTaskV2.model_validate(inputs["task"])
            task.validate_design_ownership(design)
        except Exception as exc:
            return False, {}, {}, "invalid simulation inputs: {}".format(exc)
        metrics: Dict[str, float] = {}
        points = []
        for index, point in enumerate(task.operating_points):
            try:
                point_metrics, point_raw = self._solve_point(design, task, point)
            except Exception as exc:
                return False, metrics, {"operating_points": points}, "operating point {!r} failed: {}: {}".format(point.name, type(exc).__name__, exc)
            prefix = "" if index == 0 else point.name + "."
            metrics.update({prefix + key: value for key, value in point_metrics.items()})
            points.append(point_raw)
        raw = {
            "simulator_version": self.VERSION,
            "physics_profile": dict(profile_id=task.physics.physics_profile, **AUNGIER_PROFILES[task.physics.physics_profile]),
            "operating_points": points,
            "span_fractions": list(SPAN_FRACTIONS),
        }
        return True, metrics, raw, ""

    # ------------------------------------------------------------ build
    @staticmethod
    def throat_over_pitch(row, stations) -> List[float]:
        """o/s of the constructed cascade at the row's eleven sections (Aungier section 4.9).

        Each section sits at its span fraction on the row's mid-chord plane,
        with pitch 2 pi r / Z; computed once per row, as Aungier does.
        """
        from .correlations.aungier import camberline_angles
        from .correlations.blade_geometry import throat_opening_ratio_geometric

        x = 0.5 * (row.leading_edge_axial_m + row.trailing_edge_axial_m)
        z = [s.axial_m for s in stations]
        hub = float(np.interp(x, z, [s.hub_radius_m for s in stations]))
        shroud = float(np.interp(x, z, [s.shroud_radius_m for s in stations]))
        k_in, k_out = np.asarray(row.metal_angle_in_deg), np.asarray(row.metal_angle_out_deg)
        sign = 1.0 if np.mean(k_in - k_out) > 0.0 else -1.0  # the cascade frame of the correlations
        ratios = []
        for k, span in enumerate(SPAN_FRACTIONS):
            camber = sign * (k_in[k] - k_out[k])
            chi1, _ = camberline_angles(camber, row.max_camber_location)
            stagger = sign * k_in[k] - float(chi1)
            solidity = row.chord_m[k] * row.blade_count / (2.0 * math.pi * (hub + span * (shroud - hub)))
            ratios.append(throat_opening_ratio_geometric(row.profile, row.camberline, camber, stagger, row.thickness_to_chord[k], solidity,
                                                         row.max_camber_location, row.edge_radius_to_chord))
        return ratios

    @staticmethod
    def build(design: ThroughflowDesignV2, task: ThroughflowTaskV2, point):
        """The solver problem of one operating point: (Throughflow, row models by row_id)."""
        from .solver import Annulus, InletCondition, PerfectGas, QuasiNormals, Throughflow
        from .solver.aungier_row import AungierCompressorRow, BladeSections, ShroudSeal, TipClearance
        from .solver.endwall import EndwallBoundaryLayers

        profile = AUNGIER_PROFILES[task.physics.physics_profile]
        gas = PerfectGas(cp=task.gas.cp_j_kg_k, R=task.gas.gas_constant_j_kg_k)
        stations = design.passage.stations
        annulus = Annulus.from_points([(s.axial_m, s.hub_radius_m) for s in stations], [(s.axial_m, s.shroud_radius_m) for s in stations])
        z = [stations[0].axial_m]
        for row in design.rows:
            z += [row.leading_edge_axial_m, row.trailing_edge_axial_m]
        z.append(stations[-1].axial_m)
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
                K1=profile["K1"], max_loss=profile["max_loss"], smoothing=profile["smoothing"], shock_mean=profile["shock_mean"],
            )
            models[row.row_id] = model
            rows.append(model.blade_row(row.row_id, 1 + 2 * k))
        endwall = EndwallBoundaryLayers(inlet_blockage=task.physics.inlet_blockage) if profile["endwall"] else None
        inlet = InletCondition(P0=task.inlet.total_pressure_pa, T0=task.inlet.total_temperature_k, alpha_deg=task.inlet.flow_angle_deg)
        flow = Throughflow(annulus, qn, inlet, point.mass_flow_kg_s, rows=rows, gas=gas, stream_surfaces=task.numerics.stream_surfaces,
                           curvature=task.numerics.curvature, endwall=endwall)
        return flow, models

    # ------------------------------------------------------------ solve
    def _solve_point(self, design, task, point):
        from .solver import averaged_total_state, polytropic_efficiency

        flow, models = self.build(design, task, point)
        # B* = 16, the top of the 8 to 16 range Aungier gives for Novak's damping (section 12.4);
        # (7-59) still lowers it whenever the stream-surface movement grows.
        sol = flow.solve(tol=task.numerics.tolerance, max_iterations=task.numerics.max_iterations, b_star=16.0)
        if not sol.convergence.converged:
            raise RuntimeError("the throughflow solution did not converge in {} iterations (last changes {:.3e}, {:.3e})".format(
                sol.convergence.iterations, sol.convergence.position_change[-1], sol.convergence.velocity_change[-1]))
        gas = flow.gas
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
        index = {row.row_id: k for k, row in enumerate(design.rows)}
        for stage_id in dict.fromkeys(r.stage_id for r in design.rows if r.stage_id is not None):
            members = [index[r.row_id] for r in design.rows if r.stage_id == stage_id]
            a, b = sol.stations[1 + 2 * min(members)], sol.stations[2 + 2 * max(members)]
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
            "rows": row_data,
            "stages": stage_data,
            "blockage": _finite_list(1.0 - sol.blockage),
            "exit_span": {
                "span_fraction": _finite_list(last.t),
                "total_pressure_pa": _finite_list(last.P0),
                "total_temperature_k": _finite_list(last.T0),
                "flow_angle_deg": _finite_list(np.degrees(last.alpha)),
                "meridional_velocity_m_s": _finite_list(last.Wm),
            },
            "convergence": {"iterations": sol.convergence.iterations, "position_change": sol.convergence.position_change[-1],
                            "velocity_change": sol.convergence.velocity_change[-1]},
        }
        return metrics, raw
