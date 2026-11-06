"""Structured failure evidence without changing the sm-core status contract."""
import math


class SolverError(RuntimeError):
    def __init__(self, message, *, kind="numerical_failure", component=None, station=None,
                 row=None, iterations=None, residual=None, details=None, effort=None, attempts=None):
        super().__init__(message)
        self.diagnostics = {"kind": kind, "message": message}
        for key, value in dict(component=component, station=station, row=row,
                               iterations=iterations, residual=residual).items():
            if value is not None:
                self.diagnostics[key] = float(value) if key == "residual" and math.isfinite(value) else value
        if residual is not None and not math.isfinite(residual):
            self.diagnostics["residual"] = None
        if details is not None:
            self.diagnostics["details"] = details
        if effort is not None:
            self.diagnostics["effort"] = effort
        if attempts is not None:
            self.diagnostics["attempts"] = attempts


class PhysicalStateError(SolverError):
    def __init__(self, message, **kwargs):
        super().__init__(message, kind="invalid_physical_state", **kwargs)
