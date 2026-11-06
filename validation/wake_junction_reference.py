"""Common-edge low-speed wake junction and momentum compatibility check.

Fidkowski (2021), DOI 10.2514/1.J061341, eqs. 5 and 14. The momentum
march uses the incompressible, zero wall-shear wake limit of eq. 5.
The supplied shape includes any dead-air gap. A common local edge
state is required for the additive junction. A finite stationary gap
contributes displacement and no momentum or kinetic-energy deficit.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator


@dataclass(frozen=True)
class WakeMoments:
    """Integral lengths measured against one common positive edge speed."""
    displacement: float
    momentum: float
    kinetic_energy: float

    def __post_init__(self):
        if (not all(np.isfinite(v) for v in (self.displacement, self.momentum, self.kinetic_energy))
                or not 0 < self.momentum <= self.displacement
                or not self.momentum <= self.kinetic_energy <= 2 * self.momentum):
            raise ValueError("positive realizable wake integral bounds required")


def join(pressure: WakeMoments, suction: WakeMoments, *, dead_gap=0.):
    """Sum integral defects at a common plane with equal edge state.

    The caller projects both surfaces and the gap onto that plane.
    The kinetic moment follows from adding the two profile integrals.
    This does not supply the base-pressure force on a blunt edge.
    """
    if not np.isfinite(dead_gap) or dead_gap < 0:
        raise ValueError("a finite nonnegative dead gap is required")
    return WakeMoments(
        pressure.displacement + suction.displacement + dead_gap,
        pressure.momentum + suction.momentum,
        pressure.kinetic_energy + suction.kinetic_energy,
    )


def pressure_deficits(wake: WakeMoments, width):
    """Return survey and mixed deficits divided by the edge dynamic head.

    Incompressible, parallel mean flow on a constant-width plane with
    uniform static pressure. Normalize speed by edge speed. Its first
    three area moments follow from displacement, momentum and kinetic
    thickness. Conservation of mass and normal momentum fixes the
    mixed speed and pressure, independently of a selected profile shape.
    """
    if not np.isfinite(width) or width <= wake.displacement:
        raise ValueError("width must exceed displacement")
    mean = 1 - wake.displacement / width
    second = 1 - (wake.displacement + wake.momentum) / width
    third = 1 - (wake.displacement + wake.kinetic_energy) / width
    # A nonnegative profile bounded by the edge speed has positive
    # variance, a log-convex moment sequence and q³ <= q² <= q.
    if (second < mean**2 - 1e-14 or third * mean < second**2 - 1e-14
            or (mean - second)**2 > (1 - mean) * (second - third) + 1e-14):
        raise ValueError("integrals cannot represent a wake on the supplied width")
    survey = 1 - third / mean
    mixed = 1 - 2 * second + mean**2
    return survey, mixed


def march_momentum(arc, edge_speed, shape, initial_theta):
    """Advance free-wake momentum thickness for supplied edge and shape.

    The zero-friction equation is d ln(theta) = -(2 + H) d ln(Ue).
    Both edge speed and shape are interpolated without overshoot. The
    returned array includes the given initial state.
    """
    x, speed, shape = (np.asarray(v, dtype=float) for v in (arc, edge_speed, shape))
    if (x.ndim != 1 or x.size < 2 or x.shape != speed.shape or x.shape != shape.shape
            or not np.all(np.isfinite((x, speed, shape))) or np.any(np.diff(x) <= 0)
            or np.any(speed <= 0) or np.any(shape < 1)
            or not np.isfinite(initial_theta) or initial_theta <= 0):
        raise ValueError("ordered wake stations and physical edge, shape and momentum required")
    log_edge = PchipInterpolator(x, np.log(speed)).derivative()
    profile_shape = PchipInterpolator(x, shape)
    increments = [quad(lambda s: -(2 + profile_shape(s)) * log_edge(s), a, b,
                       epsabs=1e-11, epsrel=1e-11)[0] for a, b in zip(x[:-1], x[1:])]
    return initial_theta * np.exp(np.r_[0., np.cumsum(increments)])
