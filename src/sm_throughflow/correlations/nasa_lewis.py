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

    The design code applies it to an "equivalent camber", the camber of a
    two-dimensional element with the same circulation at equal axial velocity
    and radius; the model here takes the blade camber and treats the change
    of axial velocity separately, as Aungier's off-design deviation does.
    """
    return carter_deviation_coefficient(stagger, a_c) * np.asarray(camber, dtype=float) / np.sqrt(np.asarray(solidity, dtype=float))
