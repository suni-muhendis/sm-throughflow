"""Level of spanwise mixing in a multistage axial compressor (Gallimore and Cumpsty, 1986).

S. J. Gallimore and N. A. Cumpsty, "Spanwise Mixing in Multistage Axial Flow
Compressors: Part I - Experimental Investigation", J. Turbomachinery 108
(1986) 2-9, section "A Method of Predicting the Mixing Coefficient", p. 8.

In a repeating stage the turbulence produced by the stage drag balances its
decay, Delta P_L V_z s h = (3/2) q^3 rho s h L_s / l (5); with the eddy
viscosity nu = A q l (6), the length scale l of the order of the blade
thickness t (7) and a turbulent Schmidt number of one (epsilon = nu), the
mixing coefficient nondimensionalized by axial velocity and axial stage
length is (9)

    epsilon / (V_z L_s) = (A t / L_s) [2 omega (t / L_s) / (3 phi^2)]^(1/3)

with omega = Delta P_L / (rho U_m^2) the stage loss in static-pressure rise
(ideal minus actual), phi = V_z / U_m, and A = [u'v' / q^2]^(1/2) (10) about
0.4 from u'v'/q^2 of about 0.2 near walls. The authors call the analysis
"very approximate" and good "to within a factor of about two"; eq. (9) gives
1.6e-3 and 2.1e-3 for their two low-speed four-stage compressors against
1.8e-3 and 3.8e-3 measured with tracer gas (Table 2). Part II (J.
Turbomachinery 108 (1986) 10-16, Fig. 9) finds the throughflow result
insensitive to the mixing level within a factor of two or three.
"""

#: A = (u'v'/q^2)^(1/2) with u'v'/q^2 = 0.2 (Part I, eq. 10 and the text below it).
A_DEFAULT = 0.4


def mixing_coefficient_ratio(loss: float, thickness_to_length: float, flow_coefficient: float, A: float = A_DEFAULT) -> float:
    """epsilon / (V_z L_s) from eq. (9) of Part I.

    ``loss`` is omega = Delta P_L / (rho U_m^2), ``thickness_to_length`` is
    t / L_s and ``flow_coefficient`` is phi = V_z / U_m.
    """
    if loss <= 0.0 or thickness_to_length <= 0.0 or flow_coefficient <= 0.0:
        return 0.0
    return A * thickness_to_length * (2.0 * loss * thickness_to_length / (3.0 * flow_coefficient ** 2)) ** (1.0 / 3.0)
