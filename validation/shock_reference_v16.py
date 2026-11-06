"""Research transcription of Schobeiri (1997), Part I, eqs. 42-52.

Angles here are from axial, unlike the paper's circumferential convention.
The circular-arc reference is generalized to a supplied planar meanline;
this is an unqualified hypothesis, not the production shock closure. Sharp
leading edges, uniform shock-face state, approximate pressure-force
cancellation and conserved relative stagnation temperature are assumed.
Rotation, detached bow shocks and shock/boundary-layer interaction are absent.
"""
import numpy as np
from functools import lru_cache
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from sm_throughflow.correlations import aungier as A


@lru_cache(maxsize=8)
def _inverse_grid(gamma):
    mach=1.+np.geomspace(1e-9,100.,16385)
    return A.prandtl_meyer_angle(mach,gamma),mach


def inverse_pm(nu,gamma):
    nu=np.asarray(nu,dtype=float)
    limit=90.*(np.sqrt((gamma+1.)/(gamma-1.))-1.)
    if not np.all(np.isfinite(nu)) or np.any(nu<0.) or np.any(nu>=limit):
        raise ValueError('Prandtl-Meyer angle outside finite expansion domain')
    grid,mach=_inverse_grid(gamma)
    if np.any(nu>grid[-1]):
        return A.mach_from_prandtl_meyer_angle(nu,gamma)
    value=np.interp(nu,grid,mach)
    for _ in range(3):
        derivative=np.degrees(np.sqrt(np.maximum(value*value-1.,1e-30))/(value*(1.+.5*(gamma-1.)*value*value)))
        value=np.maximum(1.,value-(A.prandtl_meyer_angle(value,gamma)-nu)/derivative)
    return np.where(nu==0.,1.,value)


def circular_arc(kappa, radius, turning, points=401):
    angle = np.radians(np.linspace(0., turning, points))
    kappa = np.radians(kappa)
    return radius*np.column_stack((np.sin(kappa)-np.sin(kappa-angle),
                                    np.cos(kappa-angle)-np.cos(kappa)))


def shock(mach, beta, curve, height_ratio=1., gamma=1.4):
    """Solve continuity, PM expansion and tangential momentum along a meanline.

    Curve units are pitch. The meanline point is the midpoint of the shock
    face, so the shock vector is (2*x, 2*y - 1). Height varies linearly to
    the supplied exit/inlet height ratio. All admissible roots are returned;
    no best-fit root selection or silent fallback is used.
    """
    if mach <= 1.:
        return dict(status='subsonic', loss=0., roots=[])
    curve = np.asarray(curve, dtype=float)
    arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))]
    spline = CubicSpline(arc, curve)
    beta = np.radians(beta)
    head = 1.-(1.+.5*(gamma-1.)*mach**2)**(-gamma/(gamma-1.))
    nu1 = float(A.prandtl_meyer_angle(mach, gamma))

    def state(s):
        p, tangent = spline(s), spline(s, 1)
        local = np.arctan2(tangent[..., 1], tangent[..., 0])
        nu = nu1 + np.degrees(beta-local)
        # Compression from the inlet is outside this expansion model.
        valid = nu >= nu1
        ms = inverse_pm(np.maximum(nu, nu1), gamma)
        temp_ratio = (1.+.5*(gamma-1.)*mach**2)/(1.+.5*(gamma-1.)*ms**2)
        vratio = mach/ms/np.sqrt(temp_ratio)
        ks = np.arcsin(vratio*np.sin(beta))  # eq. 47
        area = (1.-2*p[..., 1])*np.cos(ks)+2*p[..., 0]*np.sin(ks)
        height = 1.+(height_ratio-1.)*p[..., 0]/curve[-1, 0]
        massratio = ms/mach*temp_ratio**((gamma+1.)/(2.*(gamma-1.)))
        residual = height*area*massratio-np.cos(beta)  # eq. 42
        length = np.hypot(2*p[..., 0], 1.-2*p[..., 1])
        mn = ms*area/length  # eq. 43
        return residual, valid, ms, mn, local, ks, p

    # Exclude the collapsed zero-length expansion root at a tangent inlet.
    samples = np.linspace(1e-6*arc[-1], arc[-1], 161)
    residual, valid, *_ = state(samples)
    roots = []
    for i in np.flatnonzero(valid[:-1] & valid[1:] & (residual[:-1]*residual[1:] < 0.)):
        s = brentq(lambda v: float(state(v)[0]), samples[i], samples[i+1], xtol=1e-13)
        f, _, ms, mn, local, ks, p = state(s)
        if mn <= 1. or 2.*p[0] > curve[-1, 0]:
            continue  # no shock, or shock foot behind the blade's trailing edge
        roots.append(dict(location_fraction=float(s/arc[-1]), expansion_deg=float(np.degrees(beta-local)),
                          mach=float(ms), normal_mach=float(mn), flow_angle_deg=float(np.degrees(ks)),
                          residual=float(f), loss=float((1.-A.normal_shock_total_pressure_ratio(mn, gamma))/head)))
    return dict(status='unique' if len(roots)==1 else 'no_root' if not roots else 'multiple_roots',
                loss=roots[0]['loss'] if len(roots)==1 else None, roots=roots)
