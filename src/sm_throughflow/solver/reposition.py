"""Bounded Type-II Anderson steps for the coupled geometry/blockage iterate.

Walker and Ni (2011), SIAM J. Numer. Anal. 49, 1715-1735. This changes the
iteration path, not the fixed-point equations or the convergence tolerance.
"""
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve


def elliptic_position_step(geo, stations, residual):
    """Approximate the inverse curvature coupling, without changing its root.

    In a locally planar subsonic passage, the mass-position residual is
    approximately -(I + Ky^-1 Km) times the displacement. Apply
    (Ky + Km)^-1 Ky to the dimensional residual, with nonuniform three-point
    negative second differences. Km includes (1-Mm^2), as in Novak damping.
    Walls have zero displacement. At the axial endpoints Km=0: their update
    equals the supplied residual, not an imposed flow boundary condition.
    This is an iteration preconditioner, not an additional physical model.
    """
    nq, ns = residual.shape
    ni = ns - 2
    radial = lil_matrix((nq * ni, nq * ni))
    axial = lil_matrix(radial.shape)
    for q in range(nq):
        for j in range(1, ns - 1):
            k = q * ni + j - 1
            left, right = np.diff(geo.y[q, j-1:j+2])
            a, b = 2 / (left * (left + right)), 2 / (right * (left + right))
            radial[k, k] = a + b
            if j > 1:
                radial[k, k-1] = -a
            if j < ns - 2:
                radial[k, k+1] = -b
            if 0 < q < nq - 1:
                left, right = np.diff(geo.m[q-1:q+2, j])
                c = 1 - min(stations[q].Wm[j] / stations[q].a[j], .95)**2
                a, b = 2*c / (left*(left+right)), 2*c / (right*(left+right))
                axial[k, k] = a + b
                axial[k, k-ni], axial[k, k+ni] = -a, -b
    height = geo.y[:, -1:]
    correction = np.zeros_like(residual)
    rhs = radial.tocsr() @ (residual * height)[:, 1:-1].ravel()
    correction[:, 1:-1] = spsolve((radial + axial).tocsr(), rhs).reshape(nq, ni)
    return correction / height


class CoupledRepositioning:
    def __init__(self, depth=40):
        self.depth = depth
        self.history = []
        self.accepted = 0
        self.rejected = 0

    def step(self, t, target, damping, blockage, next_blockage, relaxation, minimum_blockage,
             position_step=None):
        """Accelerate the same damped map; fall back to its step if inadmissible.

        Fit stored undamped residual differences, also when the spatial
        preconditioner changes between iterates. Dividing a preconditioned
        difference by the current diagonal damping is not that difference.
        The caller must still test the actual undamped residual and all fields.
        """
        x = np.concatenate([t.ravel(), blockage])
        if position_step is None:
            position_step = damping * (target - t)
        f = np.concatenate([position_step.ravel(), next_blockage - blockage])
        raw = np.concatenate([(target-t).ravel(), (next_blockage-blockage)/relaxation])
        self.history.append((x.copy(), f.copy(), raw.copy()))
        self.history = self.history[-self.depth - 1:]
        candidate = x + f
        if len(self.history) >= 3:
            dx = np.column_stack([b[0] - a[0] for a, b in zip(self.history, self.history[1:])])
            df = np.column_stack([b[1] - a[1] for a, b in zip(self.history, self.history[1:])])
            dr = np.column_stack([b[2] - a[2] for a, b in zip(self.history, self.history[1:])])
            try:
                coefficients = np.linalg.lstsq(dr, raw, rcond=1e-10)[0]
                trial = candidate - (dx + df) @ coefficients
                positions = trial[:t.size].reshape(t.shape)
                kb = trial[t.size:]
                admissible = (np.all(np.isfinite(trial)) and np.max(np.abs(positions - t)) < .03
                              and np.all(np.diff(positions, axis=1) > 0)
                              and np.all((kb >= minimum_blockage) & (kb <= 1.0)))
            except np.linalg.LinAlgError:
                admissible = False
            if admissible:
                candidate = trial
                self.accepted += 1
            else:
                self.rejected += 1
                # Drop unreliable secants after an inadmissible extrapolation.
                self.history = self.history[-1:]
        positions = candidate[:t.size].reshape(t.shape)
        positions[:, 0], positions[:, -1] = 0.0, 1.0
        return positions, candidate[t.size:].copy()
