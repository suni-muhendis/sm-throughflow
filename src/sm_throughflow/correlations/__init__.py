"""Cascade correlations for axial blade rows, independent of any flow solver.

Every function here is plain numpy on per-streamline arrays and imports no
solver, so the same correlations can serve turbo-design (through
``sm_throughflow.backend``) or any other throughflow or cascade solver.

Conventions, shared by every correlation:

- Angles are in degrees, measured from the meridional direction, in the
  *cascade frame*: the frame in which the blade's inlet metal angle kappa_in
  is not below its exit metal angle kappa_out, so camber
  theta = kappa_in - kappa_out >= 0 and the blade turns the flow toward
  smaller angles. A solver adapter maps its own signs onto this frame.
- Incidence is i = beta_in - kappa_in and deviation is
  delta = beta_out - kappa_out, where beta are flow angles in the same frame
  (relative for a rotor, absolute for a stator). Positive deviation means the
  flow turns less than the blade.
- Loss is the total-pressure loss coefficient on the inlet dynamic head,
  omega = (P0_in - P0_out) / (P0_in - P_in), relative-frame for a rotor.

Each function names its source; its tests pin it to published values or to a
worked example from that source.
"""
from .cascade import camber, carter_deviation, lieblein_diffusion_factor

__all__ = ["camber", "carter_deviation", "lieblein_diffusion_factor"]
