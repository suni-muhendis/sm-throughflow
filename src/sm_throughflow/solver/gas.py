"""Equation of state for the throughflow solver, addressed by enthalpy and entropy."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PerfectGas:
    """A thermally and calorically perfect gas (Aungier, 2003, section 2.8).

    States are addressed by specific enthalpy ``h = cp T`` and entropy ``s``,
    with ``s = 0`` at ``(T_ref, P_ref)``; every function takes and returns
    numpy arrays elementwise. A total state is the same function evaluated at
    the total enthalpy.
    """

    cp: float = 1004.5
    R: float = 287.05
    T_ref: float = 288.15
    P_ref: float = 101325.0

    @property
    def gamma(self) -> float:
        return self.cp / (self.cp - self.R)

    def temperature(self, h):
        return np.asarray(h, dtype=float) / self.cp

    def enthalpy(self, T):
        return self.cp * np.asarray(T, dtype=float)

    def pressure(self, h, s):
        """Pressure of the state with enthalpy ``h`` and entropy ``s``."""
        T = self.temperature(h)
        return self.P_ref * np.exp((self.cp * np.log(T / self.T_ref) - np.asarray(s, dtype=float)) / self.R)

    def entropy(self, h, P):
        T = self.temperature(h)
        return self.cp * np.log(T / self.T_ref) - self.R * np.log(np.asarray(P, dtype=float) / self.P_ref)

    def density(self, h, s):
        return self.pressure(h, s) / (self.R * self.temperature(h))

    def sound_speed(self, h):
        return np.sqrt(self.gamma * self.R * self.temperature(h))
