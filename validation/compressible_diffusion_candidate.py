"""Unqualified compressible-circulation attribution experiment.

Schobeiri (1997), Part I, DOI 10.1155/S1023621X9700016X,
eqs. 31/34--37: rho_inf/rho_1 = 1-M_1^2 (W_2/W_1)(W_2/W_1-1).
This linearized density correction multiplies the circulation contribution
to maximum surface velocity. Applying it to Aungier's loss and blockage
curves is an explicit HYBRID HYPOTHESIS, not the complete Schobeiri model.
No data-dependent coefficient, stage identifier or efficiency target enters.
"""
from contextlib import contextmanager
import numpy as np

from sm_throughflow.correlations import aungier as A
from sm_throughflow.solver.aungier_row import AungierCompressorRow

VERSION = 'compressible_circulation_hybrid_r1'


def density_correction(mach, velocity_ratio):
    m, v = np.broadcast_arrays(np.asarray(mach, dtype=float), np.asarray(velocity_ratio, dtype=float))
    if not np.all(np.isfinite([m, v])) or np.any(m < 0) or np.any(v <= 0):
        raise ValueError('finite nonnegative Mach and positive velocity ratio required')
    factor = 1.-m*m*v*(v-1.)
    if np.any(factor <= 0):
        raise ValueError('linearized circulation density is nonpositive')
    return factor


@contextmanager
def override():
    """Process-local pilot only; both methods restored even after failure."""
    original_call = AungierCompressorRow.__call__
    original_ratio = A.max_velocity_ratio_annular

    def replacement(self, inlet, exit, geometry):
        # This is a compressibility hypothesis, not a blade-family switch.
        wm2 = inlet.Wm if exit is None else exit.Wm
        factors = []
        def ratio(beta1, solidity, r1, ct1, r2, ct2, wm1, excess=0., alpha=.0117):
            base = original_ratio(beta1, solidity, r1, ct1, r2, ct2, wm1, excess, alpha)
            w1 = wm1/np.cos(np.radians(beta1))
            w2 = np.hypot(wm2, ct2-self.sign*self.omega*r2)
            f = density_correction(w1/inlet.a, w2/w1)
            g = np.cos(np.radians(beta1))**2/solidity*(r1*ct1-r2*ct2)/(r1*wm1)
            factors.append(f)
            return base+.61*g*(f-1.)
        A.max_velocity_ratio_annular = ratio
        try:
            result = original_call(self, inlet, exit, geometry)
        finally:
            A.max_velocity_ratio_annular = original_ratio
        result.diagnostics['research_density_correction_design'] = factors[0]
        result.diagnostics['research_density_correction_actual'] = factors[-1]
        return result

    AungierCompressorRow.__call__ = replacement
    try:
        yield
    finally:
        AungierCompressorRow.__call__ = original_call
        A.max_velocity_ratio_annular = original_ratio
