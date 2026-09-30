# Streamline-curvature throughflow solver

`sm_throughflow.solver` is the environment's own meridional throughflow
solver. It replaces NASA turbo-design as the simulator; turbo-design stays as a
cross-check. It solves compressors first and is built so that turbines use the
same core.

## Why our own solver

turbo-design's compressor solve does not conserve energy across a stator: on
NASA's own Mattingly 9.1 example a stator raises the mass-averaged T0 by
0.62 K, and at 11 streamlines the rotor exit T0 departs from the Euler work of
the solver's own velocity triangles by up to 3.6 K. Its radial-equilibrium ODE
takes dT0/dr and dP0/dr from the previous pass's static profiles, where the
streamline-curvature method carries rothalpy and entropy along stream surfaces
and solves the normal-momentum equation for Vm only (L. H. Smith, 1966;
Dixon and Hall, eq. 6.6a; Aungier, 2003, ch. 7). See
[compressor_validation.md](compressor_validation.md).

## Formulation

The method is Aungier's (*Axial-Flow Compressors*, 2003, ch. 7), after Novak
(1967) and Katsanis (1964). Equation numbers below are his.

- **Stations.** Straight quasi-normals (QN) between hub and shroud, all outside
  the blade rows (before, between and after them). A blade row lies between
  two consecutive QNs. `y` is the distance along a QN from the hub; `lambda`
  its angle to the radial direction (7-1).
- **Stream surfaces.** N surfaces (N = 11 by default: 10 stream tubes),
  including hub and shroud, each enclosing a fixed fraction of the mass flow
  (equal tubes by default). Their slope `phi` (7-2) and curvature
  `kappa_m = -dphi/dm` (7-9) come from their (z, r) coordinates with the
  three-point differences of section 7.8.
- **Transport along stream surfaces.** Between QNs without a blade row, `rC_theta`,
  rothalpy `I` (so `H`) and entropy `s` are unchanged on each stream surface
  (7-40 to 7-42). Across a blade row, rothalpy is conserved (7-47) and the row
  model supplies the exit flow angle and a total-pressure loss, which set the
  exit relative total pressure (7-49) and so the exit entropy.
- **Normal momentum on a QN.** `dWm/dy = f1 Wm + f4` (7-34), with `f1`, `f2`,
  `f3` from (7-16 to 7-18) when the swirl is known (duct QNs) or (7-19 to 7-21)
  when the relative flow angle is known (blade-row exits), and the meridional
  gradient of `Wm` from (7-29) with `1 - Mm^2 >= 0.1` (7-30). It is
  integrated in closed form (7-35, 7-36), trapezoidally between stream
  surfaces; the hub value `Wm(0)` is found by bracketing and Brent's method
  until the mass flow (7-5) is matched. Choke is flagged with (7-39). The
  term `f3 / Wm` is evaluated with the previous inner iterate of `Wm`
  instead of Aungier's stream-tube form (7-31 to 7-33); the two agree
  wherever `Wm > 0`, and a profile that needs reversed flow at the hub is
  reported as having no solution.
- **Thermodynamics.** `H' = I + (r omega)^2 / 2` (7-37), `h = H' - W^2/2`
  (7-38), statics from `(h, s)`. The first gas model is a calorically perfect
  gas; the interface takes `(h, s)` so a variable-property model can follow.
- **Outer loop.** After every QN is solved, the stream surfaces are moved to
  their mass fractions (7-54 to 7-56) with Novak's damping (7-57, `B* = 8`,
  halved toward 1 by (7-59) if the position error grows). Converged when the
  stream-surface positions and the QN solutions stop changing.
- **Curvature models** (section 7.6): `full` (streamline curvature, outer loop),
  `linear` (slope and curvature linear from hub to shroud, taken from the end
  walls), `none` (simple non-isentropic normal equilibrium). All share the
  same code; the model only changes how `phi` and `kappa_m` are obtained.
- **Blockage.** End-wall `K_B` and wake `K_W` factors enter the mass integral
  (7-5); both start at 1 and are supplied by later physics (Aungier ch. 8).
  The first implementation takes one `K_B` per quasi-normal and no `K_W`.
- **Averages.** A mass average is taken tube by tube: each stream tube's mass
  flow times the mean of its two bounding values. A quantity conserved on
  every stream surface then has exactly the same average on every
  quasi-normal, whatever the flow profile.

## Status

Implemented: perfect gas; straight quasi-normals; the three curvature models;
duct and blade-row linking with inlet- and exit-based losses; stream-surface
repositioning with Novak damping; prescribed-performance rows. Verified by
`tests/test_solver_verification.py`: uniform flow and a free vortex exactly,
a forced vortex against its closed form at second order (1.9e-4 at 11
surfaces), and in a lossless stage Euler work to 1e-8 J/kg, `H` and `s`
unchanged on every stream surface and the mass-averaged T0 across the stator
unchanged to 3e-10 K. Not yet: correlation rows, blockage models, the
environment's simulator on this solver.

## Conventions

- SI units. Angles in radians internally, degrees at the interfaces.
- `theta` positive in the direction of rotation; `omega >= 0`; `C_theta` and
  `W_theta = C_theta - omega r` in that direction. Flow angles are measured
  from the meridional direction, positive toward `+theta`:
  `tan(alpha) = C_theta / Cm`, `tan(beta') = W_theta / Wm`.
- A stator is a row with `omega = 0`; then `I = H`, `W = C`, `beta' = alpha`.

## Blade rows

A row model is called with the flow on its inlet QN (per stream surface) and
the current estimate of its exit flow, and returns, per stream surface, the
exit flow angle in the row's frame and a total-pressure loss coefficient with
its basis:

- `inlet` basis (compressor practice): `omega = (P't1 - P't2) / (P't1 - P1)`,
  applied directly by (7-49).
- `exit` basis (turbine practice): `Y = (P't1 - P't2) / (P't2 - P2)`, which
  needs the exit static pressure and is applied inside the row iteration.

Because the exit flow depends on the row's performance and vice versa, each
row is iterated with its exit QN solution, starting from `Wm2 = Wm1` (7.3).
The first row model takes prescribed angles and losses; correlation-based
models (Aungier ch. 6 for compressors; turbine sets later) plug into the same
interface and use `sm_throughflow.correlations`.

## Verification, in order

Each step is a test before the next is built.

1. Uniform axial flow in a straight annulus: `Wm = mdot / (rho A)`,
   isentropic, exact.
2. Free vortex (`rC_theta` const, uniform `H`, `s`): uniform `Wm` (Dixon 6.3).
3. Forced vortex `C_theta = K r` with uniform `H`, `s`: `Cx^2 = const - 2 K^2 r^2`
   (from Dixon 6.6a); compare with the closed form.
4. Zero-loss stator: `H` and `s` unchanged on every stream surface; the
   mass-averaged `H` conserved to round-off.
5. Zero-loss rotor: on every stream surface `H2 - H1 = omega (r2 C_theta2 - r1 C_theta1)`
   (Euler) and `s2 = s1`.
6. Mass: every stream tube carries its fraction on every QN.
7. Resolution: 11 against 21 and 41 stream surfaces.
8. Cross-checks: Mattingly 9.1 against the textbook, and against turbo-design
   where turbo-design is right (meanline).
9. Validation with measurements (NASA Rotor 37, Stage 35, 74A) once the
   correlations are in.
