"""Stable interpretation of numerical, model and physical evidence."""
from dataclasses import dataclass, field
from typing import Any


def geometry_failure_kind(message):
    """Distinguish represented-geometry defects from implementation/fit limits.

    DRC retains its existing (bool, message) API; these are its explicit named
    scope rules. Intersections, missing passage and mechanical fit remain defects.
    """
    scope_rules = ("unsupported", "cannot resolve", "correlations", "cascade data", "solidity",
                   "metal angles", "camber exceeds", "clearance is at least", "Egli's model")
    return "unsupported_geometry" if any(rule in message for rule in scope_rules) else "invalid_geometry"


def failure_evidence(exc):
    evidence = dict(getattr(exc, "diagnostics", {}))
    evidence.setdefault("kind", "unexpected_simulation_error")
    evidence.setdefault("message", str(exc))
    kind = evidence["kind"]
    evidence["classification"] = {
        "physical_capacity_exceeded": "physical_limit",
        "quasi_normal_capacity": "unresolved_capacity_limit",
        "outside_model_scope": "unsupported_condition",
        "invalid_physical_state": "invalid_state",
        "invalid_geometry": "invalid_geometry",
        "unsupported_geometry": "unsupported_condition",
        "invalid_input": "invalid_input",
        "invalid_restart": "invalid_restart",
        "numerical_failure": "numerical_failure",
    }.get(kind, "unexpected_error")
    evidence["physical_limit_established"] = kind == "physical_capacity_exceeded"
    return evidence


@dataclass
class PointOutcome:
    mass_flow: float
    converged: bool
    classification: str
    metrics: dict = field(default_factory=dict)
    diagnostics: dict = field(default_factory=dict)
    restart: Any = None
    solution: Any = None
    elapsed_seconds: float = 0.0

    def __bool__(self):
        return self.converged

    def record(self):
        # Runtime is observational telemetry, never a deterministic score input.
        return dict(mass_flow=self.mass_flow, converged=self.converged, classification=self.classification,
                    metrics=self.metrics, diagnostics=self.diagnostics, elapsed_seconds=self.elapsed_seconds)
