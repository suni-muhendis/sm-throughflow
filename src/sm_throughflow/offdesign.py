"""Deterministic off-design paths with classified outcomes and bounded searches.

Wall-clock timings live in campaign telemetry; they are not used in any decision.
Callbacks accept (mass_flow, restart) and return PointOutcome. Keeping the path
logic independent of a compressor adapter also permits analytic/failure tests.
"""
import math
from time import perf_counter

from .outcomes import PointOutcome, failure_evidence, geometry_failure_kind


class EnvironmentEvaluator:
    """One admitted design and fixed-speed task, with task-owned restart policy."""

    def __init__(self, design, task, point_index=0):
        from .contracts import ThroughflowDesignV2, ThroughflowTaskV2
        from .drc import run_drc
        from .solver.errors import SolverError
        self.design = ThroughflowDesignV2.model_validate(design)
        self.task = ThroughflowTaskV2.model_validate(task)
        self.task.validate_design_ownership(self.design)
        self.point = self.task.operating_points[point_index]
        self.admission = None
        ok, error = run_drc(self.design)
        if not ok:
            kind = geometry_failure_kind(error)
            self.admission = SolverError(error, kind=kind, component="admission")

    def __call__(self, mass_flow, restart=None):
        from .simulator import SlcAungierSimulator
        from .contracts import OperatingPointV2
        from .solver.errors import SolverError
        begun = perf_counter()
        try:
            if self.admission is not None:
                raise self.admission
            if not math.isfinite(mass_flow) or mass_flow <= 0:
                raise SolverError("mass flow must be finite and positive", kind="invalid_input")
            point = OperatingPointV2(name=self.point.name, mass_flow_kg_s=mass_flow,
                                     shaft_speed_rpm=self.point.shaft_speed_rpm)
            metrics, raw, seed = SlcAungierSimulator()._solve_point(self.design, self.task, point, restart, True)
            limits = raw["limits"]
            classification = "converged_with_model_limit" if (limits["stall_criterion_crossed"] or limits["throat_capacity_exceeded"]) else "converged"
            return PointOutcome(mass_flow, True, classification, metrics, raw, restart=seed,
                                elapsed_seconds=perf_counter() - begun)
        except Exception as exc:
            evidence = failure_evidence(exc)
            return PointOutcome(mass_flow, False, evidence["classification"], diagnostics=evidence,
                                elapsed_seconds=perf_counter() - begun)


def _flow_values(values):
    result = [float(v) for v in values]
    if not result or any(not math.isfinite(v) or v <= 0 for v in result):
        raise ValueError("map flows must be finite, positive and nonempty")
    if len(set(result)) != len(result):
        raise ValueError("map flows must be unique")
    return result


def _effort(outcome):
    d = outcome.diagnostics
    return d.get("convergence", {}).get("effort", d.get("effort", {}))


def effort_summary(outcomes):
    totals = {}
    for outcome in outcomes:
        for key, value in _effort(outcome).items():
            totals[key] = totals.get(key, 0) + value
    return dict(evaluations=len(outcomes), solver=totals,
                elapsed_seconds=sum(p.elapsed_seconds for p in outcomes))


def trace_map(evaluate, mass_flows, *, max_relative_step=.03, min_relative_step=1e-4,
              max_bridge_attempts=24, comparison_rtol=1e-5, comparison_atol=1e-7):
    """Audit cold and both continuation directions; retain every requested point.

    On failure, halve the step; on success, grow it by 1.5 up to the maximum.
    Each target has a finite bridging budget and is explicitly attempted even
    when no bridge succeeds. No performance-dependent branch selection occurs.
    """
    flows = _flow_values(mass_flows)
    if not 0 < min_relative_step <= max_relative_step or max_bridge_attempts < 1:
        raise ValueError("invalid continuation step policy")
    if comparison_rtol < 0 or comparison_atol < 0:
        raise ValueError("comparison tolerances must be nonnegative")
    calls, evaluated = [], []

    def call(m, seed, path, target):
        p = evaluate(m, None if seed is None else seed.restart)
        evaluated.append(p)
        calls.append(dict(path=path, target=target, seed_flow=None if seed is None else seed.mass_flow,
                          intermediate=m != target, **p.record()))
        return p

    paths = {"cold": {m: call(m, None, "cold", m) for m in flows}}

    def advance(seed, target, direction):
        if seed is None:
            return call(target, None, direction, target)
        sign = 1.0 if target > seed.mass_flow else -1.0
        step = min(abs(target - seed.mass_flow), max_relative_step * seed.mass_flow)
        last_target = None
        for _ in range(max_bridge_attempts):
            distance = abs(target - seed.mass_flow)
            m = target if step >= distance else seed.mass_flow + sign * step
            p = call(m, seed, direction, target)
            if m == target:
                last_target = p
                if p.converged:
                    return p
            if p.converged:
                seed = p
                step = min(step * 1.5, max_relative_step * seed.mass_flow)
            else:
                step *= .5
                if step < min_relative_step * target or p.classification in ("physical_limit", "unsupported_condition", "invalid_input", "invalid_geometry"):
                    break
        # Retain the failure at the requested flow even if the budget ended on a bridge.
        return last_target if last_target is not None else call(target, seed, direction, target)

    for direction, ordered in (("ascending", sorted(flows)), ("descending", sorted(flows, reverse=True))):
        results, seed = {}, None
        for m in ordered:
            p = paths["cold"][m] if seed is None else advance(seed, m, direction)
            results[m] = p
            if p.converged:
                seed = p
        paths[direction] = results
    points = []
    for m in flows:
        candidates = [paths[path][m] for path in ("cold", "ascending", "descending")]
        good = [p for p in candidates if p.converged]
        differences = {}
        if len(good) > 1:
            for key in good[0].metrics:
                if key in ("solver_iterations",):
                    continue
                values = [p.metrics[key] for p in good if key in p.metrics]
                spread = max(values) - min(values)
                if spread > comparison_atol + comparison_rtol * max(abs(v) for v in values):
                    differences[key] = dict(min=min(values), max=max(values), spread=spread)
        selected = good[0] if good else candidates[0]  # cold, ascending, descending priority
        points.append(dict(mass_flow=m, converged=bool(good),
                           classification="path_sensitive" if differences else selected.classification,
                           selected_path=next((path for path in paths if paths[path][m] is selected), "cold"),
                           metrics={} if differences else selected.metrics,
                           initialization_sensitive=any(p.converged != selected.converged for p in candidates),
                           path_differences=differences,
                           paths={path: paths[path][m].record() for path in paths}))
    ordered = sorted(points, key=lambda p: p["mass_flow"])
    holes = []
    good_flows = [p["mass_flow"] for p in ordered if p["converged"] and not p["path_differences"]]
    for p in ordered:
        m = p["mass_flow"]
        left, right = [x for x in good_flows if x < m], [x for x in good_flows if x > m]
        if (not p["converged"] or p["path_differences"]) and left and right:
            holes.append(dict(mass_flow=m, lower_success=max(left), upper_success=min(right), classification=p["classification"]))
    return dict(points=points, interior_holes=holes, trace=calls, effort=effort_summary(evaluated),
                policy=dict(max_relative_step=max_relative_step, min_relative_step=min_relative_step,
                            max_bridge_attempts=max_bridge_attempts, comparison_rtol=comparison_rtol,
                            comparison_atol=comparison_atol, selection="cold_then_ascending_then_descending",
                            wall_time_affects_decisions=False))


def find_upper_boundary(evaluate, start, *, relative_step=.02, tolerance=1e-3, look_ahead=3, max_probes=80):
    """Bracket a reachable-flow boundary without automatically calling it choke."""
    _flow_values([start])
    if not 0 < tolerance < relative_step or look_ahead < 0 or max_probes < 2:
        raise ValueError("invalid boundary search policy")
    probes = []

    def call(m, seed=None):
        p = evaluate(m, None if seed is None else seed.restart)
        probes.append(p)
        return p

    lower = call(float(start))
    upper = None
    if lower.converged:
        while len(probes) < max_probes:
            failures = []
            for k in range(1, look_ahead + 2):
                if len(probes) >= max_probes:
                    break
                p = call(lower.mass_flow * (1 + relative_step) ** k, lower)
                if p.converged:
                    lower = p
                    break
                failures.append(p)
            else:
                upper = failures[0]
                break
            if failures and len(failures) == look_ahead + 1:
                upper = failures[0]
                break
        while upper is not None and (upper.mass_flow - lower.mass_flow) / lower.mass_flow > tolerance and len(probes) < max_probes:
            p = call((lower.mass_flow + upper.mass_flow) / 2, lower)
            if p.converged:
                lower = p
            else:
                upper = p
    bracketed = lower.converged and upper is not None
    resolved = bracketed and (upper.mass_flow - lower.mass_flow) / lower.mass_flow <= tolerance
    physical = resolved and upper.classification == "physical_limit"
    classification = ("physical_capacity_bracket" if physical else
                      upper.classification + "_boundary" if resolved else "search_budget_exhausted" if lower.converged else "no_converged_start")
    return dict(classification=classification, physical_choke_established=bool(physical),
                model_choke_flow=lower.mass_flow if physical else None,
                lower_flow=lower.mass_flow if lower.converged else None,
                upper_flow=upper.mass_flow if upper is not None else None,
                bracket_resolved=bool(resolved), probes=[p.record() for p in probes], effort=effort_summary(probes),
                policy=dict(relative_step=relative_step, tolerance=tolerance, look_ahead=look_ahead, max_probes=max_probes))
