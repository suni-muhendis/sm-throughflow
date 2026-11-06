"""Research-only unchoked branch of Banjac et al., J. Turbomach. 144 (2022).

DOI 10.1115/1.4053852, equations 17--29, 38--43 and Appendix B/F.
This is NOT the complete published model: choked and subsonic branches,
AVDR, shock/boundary-layer interaction and internal passage shocks are absent.
Actual constructed surfaces replace the paper's simplified profile geometry.
Unsupported states are explicit; this module is not a production correlation.
All angles are degrees from axial; lengths are normalized by chord.
"""
from dataclasses import dataclass
import math

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

from sm_throughflow.correlations import aungier as A
from validation.shock_reference_v16 import inverse_pm


def sind(x):
    return np.sin(np.radians(x))


def cosd(x):
    return np.cos(np.radians(x))


def tand(x):
    return np.tan(np.radians(x))


@dataclass(frozen=True)
class Bow:
    mach: float
    sonic_angle: float
    sonic_height: float
    focus: float
    detachment: float

    def angle(self, y):
        """Hyperbola tangent; eq. B10, with the exact vertex limit."""
        b = math.sqrt(self.mach**2 - 1.)
        return np.degrees(np.arctan2(np.hypot(self.focus, b*np.asarray(y)), b*b*np.asarray(y)))


def bow(mach, radius, scale=1.):
    """Moeckel detachment as fitted in Appendix B; M is bounded there to 1.05."""
    if not (1. <= mach <= 2.5 and radius > 0 and scale >= 1):
        raise ValueError('detachment fit requires 1 <= M <= 2.5, positive radius and scale >= 1')
    m = max(1.05, mach)
    b = math.sqrt(m*m - 1.)
    lam = 11.675 + 113.905/m - 341.288*math.exp(-m)
    sig = m**.7079 * math.exp(-1.0125*(m-1.)**1.157)
    pressure = 1./(-math.expm1(-8.6418*m**-2.645))
    theta = 28.34*m**-8.764 + 61.21
    ys_ratio = 1./(1.-sig*pressure*cosd(lam))
    root = math.sqrt(b*b*tand(theta)**2 - 1.)
    c = b*(b*tand(theta)-root)
    y_body = radius*cosd(lam)*scale
    return Bow(m, lam, ys_ratio*y_body, b*ys_ratio*root*y_body,
               (ys_ratio*(c+tand(lam))-tand(lam))*y_body)


def oblique(mach, angle, gamma=1.4):
    """NACA 1135: downstream Mach, flow deflection and stagnation ratio."""
    if mach < 1. or not 0. < angle <= 90.:
        raise ValueError('invalid upstream Mach or shock inclination')
    normal = mach*sind(angle)
    if normal < 1.-1e-10:
        raise ValueError('shock inclination below Mach angle')
    normal = max(1., float(normal))
    theta = math.radians(angle)
    delta = math.atan2(2./math.tan(theta)*(normal*normal-1.),
                       mach*mach*(gamma+math.cos(2.*theta))+2.)
    downstream = math.sqrt((1.+.5*(gamma-1.)*normal**2)/(gamma*normal**2-.5*(gamma-1.))) / math.sin(theta-delta)
    return dict(mach=downstream, deflection=math.degrees(delta),
                total_ratio=float(A.normal_shock_total_pressure_ratio(normal, gamma)))


class Surface:
    """Smooth graph of a constructed suction surface in chord coordinates.

    The finite edge circle is collapsed at its tangent point, following the
    paper's singular-edge construction. Surface tangents beyond that point
    come from the supplied contour, not from fitted aerodynamic data.
    """
    def __init__(self, points, stagger, solidity, thickness, edge_radius, throat):
        p = np.asarray(points, dtype=float)
        if p.ndim != 2 or p.shape[1] != 2 or np.any(np.diff(p[:, 0]) <= 0):
            raise ValueError('suction surface must be a single-valued increasing chord graph')
        self.curve = CubicSpline(p[:, 0], p[:, 1], extrapolate=False)
        self.first, self.last = p[0, 0], p[-1, 0]
        self.stagger, self.solidity = float(stagger), float(solidity)
        self.thickness, self.edge_radius, self.throat = float(thickness), float(edge_radius), float(throat)
        self.spacing = 1./self.solidity
        self.gap = self.spacing*cosd(stagger)
        self.xk = self.spacing*sind(stagger)
        if min(self.thickness, self.edge_radius, self.gap) <= 0 or not 0 < self.throat < 1:
            raise ValueError('invalid passage dimensions')

    def state(self, x):
        x = np.clip(x, self.first, self.last)
        return self.curve(x), np.degrees(np.arctan(self.curve(x, 1)))+self.stagger

    def choke_angle(self, mach):
        """Supersonic unique-incidence estimate, eqs. 13--16 (MISES fit)."""
        if not 1. <= mach <= 2.5:
            raise ValueError('supersonic choke fit requires 1 <= M <= 2.5')
        epsilon = abs(self.state(0.)[1]-self.state(self.xk)[1])
        gamma = self.stagger
        ds = max(0., 5.4050+.2120*epsilon-.1945*gamma-.001833*epsilon*gamma+.001678*gamma**2)
        dr = max(0., 2.079+.22261*epsilon-.03531*gamma-.004292*epsilon**2-.001138*epsilon*gamma)
        return math.degrees(math.acos(self.throat))+ds+(mach-1.)/.2*dr


def _unique_root(fun, low, high):
    grid = np.linspace(low, high, 65)
    value = np.asarray([fun(x) for x in grid])
    roots = [float(grid[i]) for i in np.flatnonzero(value == 0.)]
    for i in np.flatnonzero(value[1:]*value[:-1] < 0.):
        root = brentq(fun, grid[i], grid[i+1], xtol=2e-13)
        if abs(fun(root)) < 1e-9:  # a tangent pole is not a geometric intersection
            roots.append(root)
    if len(roots) != 1:
        raise ValueError(f'passage geometry has {len(roots)} admissible intersections')
    return roots[0]


def unchoked(mach, beta, surface, gamma=1.4, *, enforce_regime=True):
    """Unchoked detached passage shock; source equations solved as residuals.

    Bracketed roots replace the source's relaxed fixed point iterations. The
    returned residuals allow independent geometric equation checks. Disabling
    regime enforcement is a labeled diagnostic, never a supported closure.
    """
    if not 1. <= mach <= 2.5:
        raise ValueError('unchoked branch only supports 1 <= inlet M <= 2.5')
    s = surface
    choke = s.choke_angle(mach)
    if enforce_regime and beta < choke:
        raise ValueError('choked branch is not implemented in this research oracle')
    bo = bow(mach, s.edge_radius)
    kss = beta+bo.sonic_angle
    y1, k1 = s.state(0.)
    ms1 = float(inverse_pm(max(0., kss-k1), gamma))
    mu1 = math.degrees(math.asin(1./ms1))
    mulim = math.degrees(math.atan2(s.gap-y1, s.xk-bo.detachment))+s.stagger-k1

    def foot_residual(x, sonic=False):
        y, k = s.state(x)
        m = 1. if sonic else float(inverse_pm(max(0., kss-k), gamma))
        mu = math.degrees(math.asin(1./m))
        return x-(s.xk-bo.detachment-(s.gap-y)*tand(s.stagger-k-mu+90.))

    if mu1 >= mulim or kss < k1:
        if foot_residual(0.) >= 0.:
            xa = 0.
        else:
            xa = _unique_root(foot_residual, 0., s.last)
        ya, ka = s.state(xa)
        if kss < ka:
            xa = _unique_root(lambda x: foot_residual(x, True), 0., s.last)
            ya, ka = s.state(xa)
            kss = float(ka)
        ma = float(inverse_pm(max(0., kss-ka), gamma))
        residual_a = foot_residual(xa)
    else:
        # At the collapsed nose, the flow direction lies on the edge circle,
        # not on the downstream suction tangent (eqs. 23--24).
        xa, ya = 0., y1
        def nose_residual(m):
            k = kss-float(A.prandtl_meyer_angle(m, gamma))
            mu = math.degrees(math.atan2(s.gap-y1, s.xk-bo.detachment))+s.stagger-k
            return m*sind(mu)-1.
        ma = _unique_root(nose_residual, 1., ms1)
        ka = kss-float(A.prandtl_meyer_angle(ma, gamma))
        residual_a = nose_residual(ma)

    scale = 1.+5.*s.gap/s.thickness*sind(max(0., beta-choke))
    bb = bow(ma, s.edge_radius, scale)
    def shock_residual(x):
        y, k = s.state(x)
        return x-(s.xk-bb.detachment+(s.gap-y)*tand(.5*(ka+k)-s.stagger))
    xd = _unique_root(shock_residual, 0., s.last)
    yd, kd = s.state(xd)
    md = float(inverse_pm(max(0., kss-kd), gamma))
    theta_d = 90.-(ka-kd)
    at_b, at_d = oblique(ma, 90., gamma), oblique(md, theta_d, gamma)
    bow_ratios = [float(A.normal_shock_total_pressure_ratio(ma*sind(bb.angle(y)), gamma))
                  for y in (0., bb.sonic_height, 2.*bb.sonic_height)]
    po = 1.-bb.sonic_height/s.gap*(2.-bow_ratios[0]/2.-bow_ratios[1]-bow_ratios[2]/2.)
    pbd = .5*(at_b['total_ratio']+at_d['total_ratio'])
    total = po*pbd
    if not 0 < total <= 1.:
        raise ValueError('bow/passage integration produced an inadmissible stagnation ratio')
    head = 1.-(1.+.5*(gamma-1.)*mach**2)**(-gamma/(gamma-1.))
    return dict(loss=(1.-total)/head, total_ratio=total, bow_ratio=po, passage_ratio=pbd,
                inlet_mach=mach, inlet_angle=beta, choke_angle=choke, regime='unchoked' if beta>=choke else 'unsupported_choked_counterfactual',
                xa=xa, xd=xd, ma=ma, md=md, md_downstream=at_d['mach'], theta_d=theta_d,
                expansion_deg=kss-kd, sonic_tangent=kss, tangent_a=float(ka), tangent_d=float(kd),
                residual_a=float(residual_a), residual_d=float(shock_residual(xd)))
