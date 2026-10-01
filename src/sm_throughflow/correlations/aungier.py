"""Axial-compressor cascade correlations of Aungier (2003), chapters 4 and 6.

R. H. Aungier, *Axial-Flow Compressors: A Strategy for Aerodynamic Design and
Analysis*, ASME Press, 2003. Equation numbers are the book's. Angles are in
degrees, as positive magnitudes in the cascade frame (camber >= 0; the blade
turns the flow from beta1 toward the smaller beta2). Everything is numpy and
elementwise. docs/compressor_correlations.md records the source of each
equation and the open points.
"""
import numpy as np

#: Profile shape factor K_sh (section 6.2).
PROFILE_SHAPE_FACTOR = {"naca65": 1.0, "c4": 1.1, "dca": 0.7}

#: Coefficient of the incidence term in W_max/W1 (6-38, 6-39).
MAX_VELOCITY_INCIDENCE_COEFFICIENT = {"naca65": 0.0117, "c4": 0.007}


def _deg(x):
    return np.radians(np.asarray(x, dtype=float))


# --------------------------------------------------------------- blade geometry
def camber_from_lift_coefficient(cl0, a_c=0.5):
    """Equivalent camber angle of a NACA-65 or A4K6 camberline: tan(theta/4) = 0.05515 C_l0 / (a/c) (4-29)."""
    return np.degrees(4.0 * np.arctan(0.05515 * np.asarray(cl0, dtype=float) / np.asarray(a_c, dtype=float)))


def lift_coefficient_from_camber(theta, a_c=0.5):
    """Inverse of (4-29)."""
    return np.tan(_deg(theta) / 4.0) * np.asarray(a_c, dtype=float) / 0.05515


def throat_opening_ratio(stagger, cl0, t_c, solidity):
    """Throat opening to pitch o/s for NACA-65 blades (4-30, 4-31)."""
    cl = np.asarray(cl0, dtype=float) ** 1.5
    phi = np.asarray(stagger, dtype=float) * (1.0 - 0.05 * cl) + 5.0 * cl - 2.0  # (4-30)
    root = np.sqrt(np.asarray(solidity, dtype=float))
    return ((1.0 - np.asarray(t_c, dtype=float) * root) * np.cos(_deg(phi))) ** root  # (4-31)


# ------------------------------------------------------------- design incidence
def thickness_incidence_factor(t_c):
    """K_t,i = (10 t_b/c)^q, q = 0.28 / [0.1 + (t_b/c)^0.3] (6-10, 6-11)."""
    t_c = np.asarray(t_c, dtype=float)
    q = 0.28 / (0.1 + t_c ** 0.3)
    return (10.0 * t_c) ** q


def design_angle_of_attack(camber, solidity, t_c=0.1, a_c=0.5, k_sh=1.0):
    """Design angle of attack alpha* (6-8, 6-9), after Herrig et al. (1957)."""
    theta = np.asarray(camber, dtype=float)
    e = 0.65 - 0.002 * theta  # (6-9)
    return (3.6 * k_sh * thickness_incidence_factor(t_c) + 0.3532 * theta * np.asarray(a_c, dtype=float) ** 0.25) * np.asarray(solidity, dtype=float) ** e


def incidence_from_angle_of_attack(alpha, stagger, kappa1):
    """i = alpha + gamma - kappa1 (6-18)."""
    return np.asarray(alpha, dtype=float) + np.asarray(stagger, dtype=float) - np.asarray(kappa1, dtype=float)


def lieblein_zero_camber_incidence(beta1, solidity):
    """(i0*)_10 for 10%-thick NACA-65 blades (6-13, 6-14)."""
    beta1 = np.asarray(beta1, dtype=float)
    sigma = np.asarray(solidity, dtype=float)
    p = 0.914 + sigma ** 3 / 160.0  # (6-14)
    return beta1 ** p / (5.0 + 46.0 * np.exp(-2.3 * sigma)) - 0.1 * sigma ** 3 * np.exp((beta1 - 70.0) / 4.0)


def lieblein_incidence_slope(beta1, solidity):
    """Slope factor n (6-15)."""
    beta1 = np.asarray(beta1, dtype=float)
    sigma = np.asarray(solidity, dtype=float)
    return 0.025 * sigma - 0.06 - (beta1 / 90.0) ** (1.0 + 1.2 * sigma) / (1.5 + 0.43 * sigma)


def lieblein_design_incidence(beta1, camber, solidity, t_c=0.1, k_sh=1.0):
    """i* = K_sh K_t,i (i0*)_10 + n theta at a given design inlet flow angle beta1 (6-12)."""
    return k_sh * thickness_incidence_factor(t_c) * lieblein_zero_camber_incidence(beta1, solidity) + lieblein_incidence_slope(beta1, solidity) * np.asarray(camber, dtype=float)


def lieblein_design_incidence_for_blade(kappa1, camber, solidity, t_c=0.1, k_sh=1.0, tol=1e-12, max_iterations=200):
    """Lieblein's i* for a blade of inlet angle kappa1, iterating beta1 = kappa1 + i* (section 6.2)."""
    kappa1 = np.asarray(kappa1, dtype=float)
    i_star = np.zeros_like(kappa1)
    for _ in range(max_iterations):
        new = lieblein_design_incidence(np.maximum(kappa1 + i_star, 0.0), camber, solidity, t_c, k_sh)
        if np.max(np.abs(new - i_star)) <= tol:
            return new
        i_star = new
    raise RuntimeError("Lieblein design incidence did not converge")


# ------------------------------------------------------------- design deviation
def thickness_deviation_factor(t_c):
    """K_t,delta = 6.25 (t_b/c) + 37.5 (t_b/c)^2 (6-25)."""
    t_c = np.asarray(t_c, dtype=float)
    return 6.25 * t_c + 37.5 * t_c ** 2


def lieblein_zero_camber_deviation(beta1, solidity):
    """(delta0*)_10 for 10%-thick NACA-65 blades (6-20)."""
    beta1 = np.asarray(beta1, dtype=float)
    sigma = np.asarray(solidity, dtype=float)
    return 0.01 * sigma * beta1 + (0.74 * sigma ** 1.9 + 3.0 * sigma) * (beta1 / 90.0) ** (1.67 + 1.09 * sigma)


def lieblein_deviation_slope(beta1, solidity, camberline="naca65"):
    """m = m_1.0 / sigma^b (6-21 to 6-24); camberline is 'naca65' or 'circular_arc'."""
    x = np.asarray(beta1, dtype=float) / 100.0
    if camberline == "naca65":
        m10 = 0.17 - 0.0333 * x + 0.333 * x ** 2  # (6-22)
    elif camberline == "circular_arc":
        m10 = 0.249 + 0.074 * x - 0.132 * x ** 2 + 0.316 * x ** 3  # (6-23)
    else:
        raise ValueError("Lieblein's deviation model has no slope for camberline {!r}".format(camberline))
    b = 0.9625 - 0.17 * x - 0.85 * x ** 3  # (6-24)
    return m10 / np.asarray(solidity, dtype=float) ** b


def lieblein_design_deviation(beta1, camber, solidity, t_c=0.1, k_sh=1.0, camberline="naca65"):
    """delta* = K_sh K_t,delta (delta0*)_10 + m theta (6-19), at the design inlet flow angle."""
    return k_sh * thickness_deviation_factor(t_c) * lieblein_zero_camber_deviation(beta1, solidity) + lieblein_deviation_slope(beta1, solidity, camberline) * np.asarray(camber, dtype=float)


def howell_design_deviation(beta1, kappa2, camber, solidity, t_c=0.1, a_c=0.5, k_sh=1.0):
    """Modified Howell design deviation (6-26), for A4K6 and parabolic-arc camberlines and inlet guide vanes."""
    theta = np.asarray(camber, dtype=float)
    root = np.sqrt(np.asarray(solidity, dtype=float))
    howell = (0.92 * np.asarray(a_c, dtype=float) ** 2 + 0.002 * np.asarray(kappa2, dtype=float)) / (1.0 - 0.002 * theta / root) * theta / root
    return howell + (k_sh * thickness_deviation_factor(t_c) - 1.0) * lieblein_zero_camber_deviation(beta1, solidity)


# ------------------------------------------------------------------ design loss
def design_loss_from_diffusion_factor(D, beta2, solidity):
    """omega* from omega* cos(beta2*)/(2 sigma) = 0.0035 [1 + 3.5 D* + 37 D*^4] (6-34); valid to D* = 0.6."""
    D = np.asarray(D, dtype=float)
    return 0.0035 * (1.0 + 3.5 * D + 37.0 * D ** 4) * 2.0 * np.asarray(solidity, dtype=float) / np.cos(_deg(beta2))


def max_velocity_ratio(beta1, beta2, solidity, incidence_excess=0.0, alpha=0.0117):
    """W_max/W1 for a two-dimensional cascade (6-35; 6-38 with the incidence term for i > i*)."""
    b1, b2 = _deg(beta1), _deg(beta2)
    excess = np.maximum(np.asarray(incidence_excess, dtype=float), 0.0)
    return 1.12 + 0.61 * np.cos(b1) ** 2 / np.asarray(solidity, dtype=float) * (np.tan(b1) - np.tan(b2)) + alpha * excess ** 1.43


def max_velocity_ratio_annular(beta1, solidity, r1, c_theta1, r2, c_theta2, c_m1, incidence_excess=0.0, alpha=0.0117):
    """W_max/W1 for an annular, possibly rotating cascade (6-39), Klapproth's form.

    The swirl velocities are absolute, in the cascade frame (their sign flipped
    for a row drawn the other way). The incidence term applies for i > i* only.
    """
    b1 = _deg(beta1)
    circulation = (np.asarray(r1, dtype=float) * np.asarray(c_theta1, dtype=float) - np.asarray(r2, dtype=float) * np.asarray(c_theta2, dtype=float)) / (np.asarray(r1, dtype=float) * np.asarray(c_m1, dtype=float))
    excess = np.maximum(np.asarray(incidence_excess, dtype=float), 0.0)
    return 1.12 + 0.61 * np.cos(b1) ** 2 / np.asarray(solidity, dtype=float) * circulation + alpha * excess ** 1.43


def equivalent_diffusion_factor(max_velocity_ratio_value, w1, w2):
    """D_eq = (W_max/W1)(W1/W2) (6-30, 6-36)."""
    return np.asarray(max_velocity_ratio_value, dtype=float) * np.asarray(w1, dtype=float) / np.asarray(w2, dtype=float)


def design_loss_from_equivalent_diffusion(D_eq, beta2, w1_over_w2, solidity, K1=0.004, K2=1.0):
    """omega* from omega* cos(beta2*)/(2 sigma) (W1/W2)^2 = K1 [K2 + 3.1 (D_eq - 1)^2 + 0.4 (D_eq - 1)^8].

    (6-46); K1 = 0.004, K2 = 1 is Lieblein's two-dimensional correlation (6-37).
    """
    x = np.asarray(D_eq, dtype=float) - 1.0
    return K1 * (K2 + 3.1 * x ** 2 + 0.4 * x ** 8) * 2.0 * np.asarray(solidity, dtype=float) / (np.cos(_deg(beta2)) * np.asarray(w1_over_w2, dtype=float) ** 2)


def endwall_loss_constant(pitch_over_height, beta2, reynolds_factor=0.0, K1=0.0073):
    """K2 = 1 + (s/h) cos(beta2) + 0.004 K_Re / K1 (6-99, 6-100)."""
    return 1.0 + np.asarray(pitch_over_height, dtype=float) * np.cos(_deg(beta2)) + 0.004 * np.asarray(reynolds_factor, dtype=float) / K1


def reynolds_loss_factor(reynolds):
    """K_Re (6-101, 6-102) from the chord Reynolds number; zero at 2.5e5."""
    re = np.asarray(reynolds, dtype=float)
    laminar = np.sqrt(2.5e5 / re) - 1.0  # (6-101)
    turbulent = (np.log(2.5e5) / np.log(re)) ** 2.58 - 1.0  # (6-102)
    return np.where(re < 2.5e5, laminar, turbulent)


# ------------------------------------------------------- stall and Mach number
def stall_angles_of_attack(alpha_star, camber, beta1_negative, beta1_positive):
    """Negative and positive stall angles of attack (6-47, 6-48), Herrig et al. (1957).

    beta1_negative is limited to at least 20 deg, as Aungier does, since (6-47)
    is singular at zero. Both depend on the stall inlet angle itself; see
    stall_angles_for_blade for the iterated form.
    """
    theta = np.asarray(camber, dtype=float)
    beta1c = np.maximum(np.asarray(beta1_negative, dtype=float), 20.0)
    alpha_c = alpha_star - 9.0 + (1.0 - (30.0 / beta1c) ** 0.48) * theta / 4.176  # (6-47)
    alpha_s = alpha_star + 10.3 + (2.92 - np.asarray(beta1_positive, dtype=float) / 15.6) * theta / 8.2  # (6-48)
    return alpha_c, alpha_s


def stall_angles_for_blade(alpha_star, camber, stagger, tol=1e-12, max_iterations=200):
    """(6-47, 6-48) solved with beta1 = alpha + gamma at each stall point."""
    stagger = np.asarray(stagger, dtype=float)
    alpha_c = np.asarray(alpha_star, dtype=float) - 9.0
    alpha_s = np.asarray(alpha_star, dtype=float) + 10.3
    for _ in range(max_iterations):
        new_c, new_s = stall_angles_of_attack(alpha_star, camber, alpha_c + stagger, alpha_s + stagger)
        if max(np.max(np.abs(new_c - alpha_c)), np.max(np.abs(new_s - alpha_s))) <= tol:
            return new_c, new_s
        alpha_c, alpha_s = new_c, new_s
    raise RuntimeError("stall angles did not converge")


def stall_incidence(i_star, range_negative, range_positive, mach, k_sh=1.0):
    """i_c and i_s narrowed by the relative inlet Mach number (6-51, 6-52), K_sh <= 1."""
    mach = np.asarray(mach, dtype=float)
    k = np.minimum(k_sh, 1.0)
    i_c = i_star - np.asarray(range_negative, dtype=float) / (1.0 + 0.5 * mach ** 3)
    i_s = i_star + np.asarray(range_positive, dtype=float) / (1.0 + 0.5 * (k * mach) ** 3)
    return i_c, i_s


def minimum_loss_incidence(i_c, i_s, range_negative, range_positive):
    """i_m = i_c + (i_s - i_c) R_c / (R_c + R_s) (6-55)."""
    return i_c + (i_s - i_c) * range_negative / (range_negative + range_positive)


def minimum_loss(omega_star, i_m, i_star, range_positive, mach=0.0, critical_mach=np.inf, sonic_to_inlet_velocity=1.0, k_sh=1.0):
    """omega_m (6-58), with the supercritical term of (6-60) when M' > M_c' (M' limited to 1)."""
    base = np.asarray(omega_star, dtype=float) * (1.0 + (i_m - i_star) ** 2 / np.asarray(range_positive, dtype=float) ** 2)
    mach = np.minimum(np.asarray(mach, dtype=float), 1.0)
    excess = np.maximum(mach / critical_mach - 1.0, 0.0)
    return base + k_sh * (excess * sonic_to_inlet_velocity) ** 2


# ------------------------------------------------------------------- shock loss
def prandtl_meyer_angle(mach, gamma=1.4):
    """Prandtl-Meyer angle nu(M) of a perfect gas, degrees (zero at M = 1)."""
    m2 = np.maximum(np.asarray(mach, dtype=float) ** 2 - 1.0, 0.0)
    k = (gamma + 1.0) / (gamma - 1.0)
    return np.degrees(np.sqrt(k) * np.arctan(np.sqrt(m2 / k)) - np.arctan(np.sqrt(m2)))


def mach_from_prandtl_meyer_angle(nu, gamma=1.4, tol=1e-13):
    """Inverse of prandtl_meyer_angle, by bisection (nu is monotonic in M)."""
    nu = np.asarray(nu, dtype=float)
    nu_max = 90.0 * (np.sqrt((gamma + 1.0) / (gamma - 1.0)) - 1.0)
    if np.any(nu < 0.0) or np.any(nu >= nu_max):
        raise ValueError("Prandtl-Meyer angle must lie in [0, {:.2f}) deg".format(nu_max))
    low, high = np.ones_like(nu), np.full_like(nu, 2.0)
    while np.any(prandtl_meyer_angle(high, gamma) < nu):
        high = np.where(prandtl_meyer_angle(high, gamma) < nu, 2.0 * high, high)
    while np.max(high - low) > tol:
        mid = 0.5 * (low + high)
        below = prandtl_meyer_angle(mid, gamma) < nu
        low, high = np.where(below, mid, low), np.where(below, high, mid)
    return 0.5 * (low + high)


def normal_shock_total_pressure_ratio(mach, gamma=1.4):
    """P0 downstream / P0 upstream of a normal shock in a perfect gas (1 for M <= 1)."""
    m2 = np.maximum(np.asarray(mach, dtype=float), 1.0) ** 2
    g = gamma
    return ((g + 1.0) * m2 / ((g - 1.0) * m2 + 2.0)) ** (g / (g - 1.0)) * ((g + 1.0) / (2.0 * g * m2 - (g - 1.0))) ** (1.0 / (g - 1.0))


def suction_surface_expansion_angle(kappa1, camber, t_c, solidity):
    """Expansion angle phi along the suction surface up to the passage shock (6-65, 6-68, 6-69).

    Double-circular-arc blade with a sharp leading edge, flow entering tangent
    to the suction surface, passage shock running from the adjacent blade's
    leading edge normal to the suction surface. The book prints (6-61) and
    (6-63) as 2R/c = sin(theta/2); the circular-arc relation (4-7) is
    c/2 = R sin(theta/2), used here. phi is limited to theta_u, the turning of
    the whole suction surface, for a shock line that would pass behind the
    trailing edge (a geometric bound the book does not state).
    """
    theta = _deg(camber)
    theta_u = 4.0 * np.arctan(np.tan(theta / 4.0) + np.asarray(t_c, dtype=float))  # (6-65)
    psi = np.pi / 2.0 - theta_u / 2.0 - _deg(kappa1) + theta / 2.0  # (6-68)
    pitch = 1.0 / np.asarray(solidity, dtype=float)  # s/c
    # (6-69) with both sides multiplied by sin(theta_u/2), so a flat plate (R_u infinite) gives phi = 0.
    sin_half = np.sin(theta_u / 2.0)
    phi = np.arctan2(pitch * np.cos(psi) * sin_half, pitch * np.sin(psi) * sin_half + 0.5)
    return np.degrees(np.minimum(phi, theta_u))


def shock_loss(mach, expansion_angle, gamma=1.4, mean="arithmetic"):
    """Passage shock loss coefficient omega_s on the inlet basis, (P't1 - P't,b)/(P't1 - P1).

    Schwenk, Lewis and Hartmann, NACA RM E57A30 (1957), appendix B, the model
    behind Miller, Lewis and Hartmann (1961), Swan (1961) and Aungier's
    section 6.7: the flow expands isentropically from the relative inlet Mach
    number M1' by the angle phi (Prandtl-Meyer, 6-70) to M_S', and the loss is
    that of a normal shock at a mean of M1' and M_S'. ``mean="arithmetic"``
    takes (M1' + M_S')/2, as the NACA report does (its worked values check
    only with this mean); ``"geometric"`` takes sqrt(M1' M_S'), as Aungier
    prints (6-71). Zero for M1' <= 1, where the method does not apply.
    """
    mach = np.asarray(mach, dtype=float)
    supersonic = mach > 1.0
    m1 = np.where(supersonic, mach, 1.0)
    nu = prandtl_meyer_angle(m1, gamma) + np.maximum(np.asarray(expansion_angle, dtype=float), 0.0)
    m_s = mach_from_prandtl_meyer_angle(nu, gamma)
    if mean == "arithmetic":
        m_in = 0.5 * (m1 + m_s)
    elif mean == "geometric":
        m_in = np.sqrt(m1 * m_s)
    else:
        raise ValueError("mean must be 'arithmetic' or 'geometric', not {!r}".format(mean))
    static_ratio = (1.0 + 0.5 * (gamma - 1.0) * m1 ** 2) ** (-gamma / (gamma - 1.0))
    omega = (1.0 - normal_shock_total_pressure_ratio(m_in, gamma)) / (1.0 - static_ratio)  # NACA (B2)
    return np.where(supersonic, omega, 0.0)


def off_design_loss(incidence, i_m, i_c, i_s, omega_m, omega_shock=0.0):
    """Loss away from minimum-loss incidence (6-78 to 6-82)."""
    i = np.asarray(incidence, dtype=float)
    xi = np.where(i >= i_m, (i - i_m) / (i_s - i_m), (i - i_m) / (i_m - i_c))  # (6-78), (6-79)
    shape = np.where(xi < -2.0, 5.0 - 4.0 * (xi + 2.0), np.where(xi > 1.0, 2.0 + 2.0 * (xi - 1.0), 1.0 + xi ** 2))
    return omega_shock + np.asarray(omega_m, dtype=float) * shape


# ------------------------------------------------------------ off-design turning
def deviation_slope(beta1, solidity):
    """(d delta / d i)* = [1 + (sigma + 0.25 sigma^4)(beta1/53)^2.5] / exp(3.1 sigma) (6-76)."""
    sigma = np.asarray(solidity, dtype=float)
    return (1.0 + (sigma + 0.25 * sigma ** 4) * (np.asarray(beta1, dtype=float) / 53.0) ** 2.5) / np.exp(3.1 * sigma)


def off_design_deviation(delta_star, slope, incidence, i_star, wm_ratio=1.0, inlet_guide_vane=False):
    """delta = delta* + (d delta/d i)* (i - i*) + 10 (1 - W_m2/W_m1) (6-77); no incidence term for IGVs."""
    incidence_term = 0.0 if inlet_guide_vane else slope * (np.asarray(incidence, dtype=float) - i_star)
    return delta_star + incidence_term + 10.0 * (1.0 - np.asarray(wm_ratio, dtype=float))


def wake_blockage(D_eq):
    """B_wake = 0 for D_eq <= 2, 1 - (2/D_eq)^0.9 above (6-83, 6-84)."""
    D_eq = np.asarray(D_eq, dtype=float)
    return np.where(D_eq <= 2.0, 0.0, 1.0 - (2.0 / np.maximum(D_eq, 2.0)) ** 0.9)
