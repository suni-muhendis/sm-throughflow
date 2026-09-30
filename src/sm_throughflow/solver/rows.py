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
    """

    exit_angle: np.ndarray
    loss: np.ndarray
    basis: LossBasis = "inlet"


# A row model sees the flow on its inlet quasi-normal and the current
# estimate of the flow on its exit quasi-normal (None on the first pass).
RowModel = Callable[[StationFlow, Optional[StationFlow], np.ndarray], RowPerformance]


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

    def __call__(self, inlet: StationFlow, exit: Optional[StationFlow], exit_t: np.ndarray) -> RowPerformance:
        return RowPerformance(
            exit_angle=np.radians(_on_span(self.exit_angle_deg, exit_t)),
            loss=_on_span(self.loss, exit_t),
            basis=self.basis,
        )
