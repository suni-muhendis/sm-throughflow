"""Blade rows between quasi-normals and the models that set their performance."""
from dataclasses import dataclass
from typing import Callable, Literal, Optional, Sequence, Union

import numpy as np

from .quasi_normal import StationFlow

LossBasis = Literal["inlet", "exit"]


@dataclass(frozen=True)
class RowPerformance:
    """What a row model returns, one value per stream surface.

    ``exit_angle`` is the exit flow angle in the row's frame (radians, from the
    meridional direction, positive toward rotation). ``loss`` is a
    total-pressure loss coefficient on ``basis``: ``inlet`` means
    (P't2,ideal - P't2) / (P't1 - P1), Aungier's (7-49); ``exit`` means
    (P't2,ideal - P't2) / (P't2 - P2), the turbine convention.
    ``wake_blockage`` is the fraction B_wake of each stream sheet's area that
    the blade wakes block at the row exit (Aungier's 7-6, K_W = 1 - B_wake);
    ``diagnostics`` carries whatever else the model reports, per stream surface.
    """

    exit_angle: np.ndarray
    loss: np.ndarray
    basis: LossBasis = "inlet"
    wake_blockage: Optional[np.ndarray] = None
    diagnostics: Optional[dict] = None


@dataclass(frozen=True)
class ExitGeometry:
    """Where the stream surfaces cross a row's exit quasi-normal: span fraction t, y, r and z."""

    t: np.ndarray
    y: np.ndarray
    r: np.ndarray
    z: np.ndarray


# A row model sees the flow on its inlet quasi-normal, the current estimate
# of the flow on its exit quasi-normal (None on the first pass) and the
# exit quasi-normal's stream-surface geometry.
RowModel = Callable[[StationFlow, Optional[StationFlow], ExitGeometry], RowPerformance]


@dataclass(frozen=True)
class BladeRow:
    """A blade row between quasi-normals ``inlet`` and ``inlet + 1``.

    ``omega`` is the rotational speed in rad/s (0 for a stator).
    """

    name: str
    inlet: int
    omega: float
    model: RowModel


def _on_span(values, t):
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == 1:
        return np.full_like(t, values.item())
    return np.interp(t, np.linspace(0.0, 1.0, values.size), values)


class PrescribedRow:
    """Exit angle and loss given directly, as values at evenly spaced span fractions."""

    def __init__(self, exit_angle_deg: Union[float, Sequence[float]], loss: Union[float, Sequence[float]] = 0.0, basis: LossBasis = "inlet"):
        self.exit_angle_deg = exit_angle_deg
        self.loss = loss
        self.basis = basis

    def __call__(self, inlet: StationFlow, exit: Optional[StationFlow], geometry: ExitGeometry) -> RowPerformance:
        return RowPerformance(
            exit_angle=np.radians(_on_span(self.exit_angle_deg, geometry.t)),
            loss=_on_span(self.loss, geometry.t),
            basis=self.basis,
        )
