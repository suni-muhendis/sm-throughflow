"""Conservative integration of the discontinuous passage-shock closure.

The NACA/Aungier supersonic formula has a finite right limit at M=1 for
nonzero expansion. Sampling it only at stream surfaces causes a finite jump
when a sonic contour crosses a node. Integrate its pressure defect over each
dual mass cell, splitting at M=1, instead. No subsonic shock correlation or
Mach smoothing width is introduced. This is a versioned span discretization.
"""
import numpy as np

from ..correlations.aungier import shock_loss

_NODES, _WEIGHTS = np.polynomial.legendre.leggauss(4)


def integrated_shock_loss(mach, turning, head, tube_mass, gamma=1.4, mean="arithmetic"):
    """Dual-cell mean pressure defect divided by the node's inlet dynamic head.

    Interpolate M, turning and dynamic head linearly in cumulative inlet
    mass. Cell boundaries bisect neighboring mass coordinates, so their
    masses equal the nodal trapezoid weights. Four-point Gauss quadrature
    acts separately on each smooth subinterval, including any sonic cut.
    The weighted sum of returned pressure defects equals the integrated
    defect to quadrature accuracy. Existing downstream loss smoothing and
    limiting are separate operations and may change that integral.

    A uniformly sonic span remains a discontinuity of the underlying
    empirical closure; cell integration does not qualify that closure.
    """
    mach, turning, head, tube_mass = [np.asarray(v, dtype=float) for v in (mach, turning, head, tube_mass)]
    if (mach.ndim != 1 or len(mach) < 2 or turning.shape != mach.shape or head.shape != mach.shape
            or tube_mass.shape != (len(mach)-1,) or not all(np.all(np.isfinite(v)) for v in (mach, turning, head, tube_mass))
            or np.any(mach < 0) or np.any(head <= 0) or np.any(tube_mass <= 0)):
        raise ValueError("shock integration needs finite span fields, positive head and positive tube masses")
    if np.all(mach <= 1.):
        return np.zeros_like(mach)
    x = np.r_[0., np.cumsum(tube_mass)]
    x /= x[-1]
    edges = np.r_[0., .5*(x[1:]+x[:-1]), 1.]
    crossed = (mach[:-1]-1.)*(mach[1:]-1.) < 0.
    sonic = x[:-1][crossed] + (1.-mach[:-1][crossed])*np.diff(x)[crossed]/np.diff(mach)[crossed]
    knots = np.unique(np.r_[x, edges, sonic])
    lo, hi = knots[:-1], knots[1:]
    q = .5*(lo+hi)[:, None] + .5*(hi-lo)[:, None]*_NODES
    pressure_defect = shock_loss(np.interp(q, x, mach), np.interp(q, x, turning), gamma, mean)*np.interp(q, x, head)
    integrals = .5*(hi-lo)*np.sum(pressure_defect*_WEIGHTS, axis=1)
    cell = np.searchsorted(edges, .5*(lo+hi), side="right")-1
    values = np.bincount(cell, weights=integrals, minlength=len(mach))
    return values/np.diff(edges)/head
