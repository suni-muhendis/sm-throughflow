"""Correlations of the NASA Lewis compressor design system, for the blade sections it designed.

The multiple-circular-arc rows of the NASA Lewis transonic stages (stages 35
to 38, rotor 67 and others) were designed with the Lewis design code (J. E.
Crouse, NASA TN D-7345, 1974; J. E. Crouse and W. T. Gorrell, NASA TP-1946,
1981). Its deviation rule is used here for those sections, in place of the
rules Aungier fits to NACA 65 and circular-arc cascades.
"""
import numpy as np


def carter_deviation_coefficient(stagger, a_c):
    """Carter's m as the Lewis design code fits it (TN D-7345 eq. 21; NASA TM X-2379, printed p. 4).

    m = x (2 a/c)^y, x = 0.219 + 0.0008916 gamma + 0.000027085 gamma^2,
    y = 2.175 - 0.035528 gamma + 0.00019167 gamma^2, gamma the setting angle
    in degrees and a/c the chordwise position of maximum camber; fitted to
    the curves of Carter and Hughes (ARC R&M 2384). TN D-7345 prints the
    coefficients rounded (0.00002708, 0.03552, 0.0001917); TM X-2379 gives
    the digits used here. At a/c = 0.5 it is Carter's rule for a circular arc.
    """
    gamma = np.abs(np.asarray(stagger, dtype=float))
    x = 0.219 + 0.0008916 * gamma + 0.000027085 * gamma ** 2
    y = 2.175 - 0.035528 * gamma + 0.00019167 * gamma ** 2
    return x * (2.0 * np.asarray(a_c, dtype=float)) ** y


def carter_deviation(camber, stagger, a_c, solidity):
    """delta = m theta / sqrt(sigma) (TN D-7345 eq. 20), degrees.

    This is the equal-meridional-velocity, constant-radius cascade limit.
    Use annular_carter_deviation for a row with changing radius or velocity.
    """
    return carter_deviation_coefficient(stagger, a_c) * np.asarray(camber, dtype=float) / np.sqrt(np.asarray(solidity, dtype=float))


def annular_carter_deviation(kappa1, kappa2, stagger, a_c, solidity,
                            wm1, wm2, r1, r2, signed_omega=0.0):
    """Invert the equivalent-camber rule of TN D-7345 for a known blade.

    BLADE, printed pp. 144 and 147 (lines 71-73 and 224-230), transports
    exit absolute angular momentum to the inlet radius and meridional speed.
    In the positive-camber cascade frame, q = m/sqrt(sigma), b = kappa2+delta:

      tan(b_eq) = (r2/r1)(wm2/wm1)tan(b)
                  + signed_omega*(r2**2-r1**2)/(r1*wm1)
      delta = q*(kappa1-b_eq)/(1-q).

    The source's design-mode DKAPPA is the equivalent camber, not the actual
    metal-angle difference. Its inverse is the unique root of
    (1-q)*(b-kappa2)+q*(b_eq-kappa1)=0 for 0<=q<1, positive velocities/radii,
    and metal angles strictly between -90 and 90 degrees. No fitted radius
    or velocity coefficient is introduced. signed_omega is omega times the
    solver-to-cascade sign. Off-design incidence is not included here.
    """
    values = np.broadcast_arrays(*[np.asarray(v, dtype=float) for v in
        (kappa1, kappa2, stagger, a_c, solidity, wm1, wm2, r1, r2, signed_omega)])
    k1, k2, gamma, ac, sigma, v1, v2, radius1, radius2, rotation = values
    if (not all(np.all(np.isfinite(v)) for v in values)
            or np.any(np.abs(k1) >= 90.) or np.any(np.abs(k2) >= 90.) or np.any(np.abs(gamma) >= 90.)
            or np.any((ac <= 0.) | (ac > 1.))
            or any(np.any(v <= 0.) for v in (sigma, v1, v2, radius1, radius2))):
        raise ValueError('annular Carter requires finite angles within (-90,90), positive velocities/radii/solidity and 0<a/c<=1')
    q = carter_deviation_coefficient(gamma, ac) / np.sqrt(sigma)
    if np.any((q < 0.) | (q >= 1.)):
        raise ValueError('annular Carter requires 0 <= m/sqrt(sigma) < 1')
    a = (radius2/radius1)*(v2/v1)
    b = rotation*(radius2-radius1)*(radius2+radius1)/(radius1*v1)
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError('annular Carter velocity transformation is non-finite')
    lo, hi = np.full_like(q, -90.), np.full_like(q, 90.)
    # The derivative is (1-q)+q*a*sec(beta)^2/(1+(a*tan(beta)+b)^2)>0.
    # Fixed bisection is deterministic, and does not depend on a prior iterate.
    for _ in range(54):
        beta = .5*(lo+hi)
        equivalent = np.degrees(np.arctan(a*np.tan(np.radians(beta))+b))
        residual = (1.-q)*(beta-k2)+q*(equivalent-k1)
        lo = np.where(residual < 0., beta, lo)
        hi = np.where(residual >= 0., beta, hi)
    return .5*(lo+hi)-k2
