"""Streamline-curvature throughflow solver (Aungier, 2003, ch. 7).

See docs/throughflow_solver.md for the formulation and its conventions.
"""
from .gas import PerfectGas
from .geometry import CURVATURE_MODELS, Annulus, QuasiNormals
from .quasi_normal import ChokedError, StationFlow
from .rows import BladeRow, PrescribedRow, RowPerformance
from .throughflow import InletCondition, Throughflow, ThroughflowSolution

__all__ = [
    "Annulus",
    "BladeRow",
    "CURVATURE_MODELS",
    "ChokedError",
    "InletCondition",
    "PerfectGas",
    "PrescribedRow",
    "QuasiNormals",
    "RowPerformance",
    "StationFlow",
    "Throughflow",
    "ThroughflowSolution",
]
