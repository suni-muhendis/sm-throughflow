"""Basic cascade relations: camber, Carter's deviation rule, Lieblein's diffusion factor."""
import numpy as np


def camber(kappa_in, kappa_out):
    """Blade camber theta = kappa_in - kappa_out, degrees (cascade frame)."""
    return np.asarray(kappa_in, dtype=float) - np.asarray(kappa_out, dtype=float)


def carter_deviation(kappa_in, kappa_out, solidity, m=0.25):
    """Carter's rule, delta = m * theta / sqrt(sigma), degrees.

    A. D. S. Carter, 1950 (Aeronautical Research Council; report number to be
    confirmed against the original), in the form given by S. L. Dixon and
    C. A. Hall, *Fluid Mechanics and Thermodynamics of Turbomachinery*, in
    the two-dimensional cascades chapter. ``m`` depends on stagger and profile
    shape; 0.25 is the value NASA turbo-design and the classical textbook
    form use.
    """
    sigma = np.maximum(np.asarray(solidity, dtype=float), 1e-6)
    return m * camber(kappa_in, kappa_out) / np.sqrt(sigma)


def lieblein_diffusion_factor(w_in, w_out, delta_w_theta, solidity):
    """Lieblein's diffusion factor D = 1 - W2/W1 + |dW_theta| / (2 sigma W1).

    S. Lieblein, F. C. Schwenk and R. L. Broderick, "Diffusion factor for
    estimating losses and limiting blade loadings in axial-flow-compressor
    blade elements", NACA RM E53D01, 1953. Velocities in the blade's frame
    (relative for a rotor).
    """
    w_in = np.asarray(w_in, dtype=float)
    sigma = np.maximum(np.asarray(solidity, dtype=float), 1e-6)
    return 1.0 - np.asarray(w_out, dtype=float) / w_in + np.abs(delta_w_theta) / (2.0 * sigma * w_in)
