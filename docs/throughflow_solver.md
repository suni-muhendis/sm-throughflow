# Streamline-curvature throughflow solver

`sm_throughflow.solver` is the environment's own meridional throughflow
solver. It replaced NASA turbo-design as the simulator (the turbo-design path
was later removed from the package; the comparisons below were made while it
was still installed). It solves compressors first and is built so that
turbines use the same core.

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
  its angle to the radial direction (7-1). In v9, interior row wall vertices
  remain geometric controls without additional flow states. Stream-surface
  annulus fraction is interpolated between solved stations; wall-constrained
  paths determine arc length, slope and curvature. Interior annulus throats
  below both edge areas remain unsupported.
- **Stream surfaces.** N surfaces (N = 11 by default: 10 stream tubes),
  including hub and shroud, each enclosing a fixed fraction of the mass flow
  (equal tubes by default). Their slope `phi` (7-2) and curvature
  `kappa_m = -dphi/dm` (7-9) come from local parametric quadratic fits to
  their (z, r) coordinates in v11, including one-sided endpoint fits. Direct
  second differences replace the old composition of centered first differences.
- **Transport along stream surfaces.** Between QNs without a blade row, `rC_theta`,
  rothalpy `I` (so `H`) and entropy `s` are unchanged on each stream surface
  (7-40 to 7-42). Across a blade row, rothalpy is conserved (7-47) and the row
  model supplies the exit flow angle and a total-pressure loss, which set the
  exit relative total pressure (7-49) and so the exit entropy.
- **Normal momentum on a QN.** `dWm/dy = f1 Wm + f4` (7-34), with `f1`, `f2`,
  `f3` from (7-16 to 7-18) when the swirl is known (duct QNs) or (7-19 to 7-21)
  when the relative flow angle is known (blade-row exits), and the meridional
  gradient of `Wm` from (7-29) with `1 - Mm^2 >= 0.1` (7-30). It is
  integrated in v9 using `u = Wm^2`: `u' = 2 f1 u + 2 f2 sqrt(u) + 2 f3`,
  with `f2 = 0` for known swirl. An integrating factor for `2 f1` and a
  trapezoidal integral of the remaining forcing remove the lagged `f3/Wm`
  singularity. Coefficients still iterate to the unrelaxed velocity tolerance.
  This is algebraically the same continuous equation but a different discrete
  operator from v8; separate reference values and campaigns are required.
  Hub speed is bracketed in both directions when the starting profile is
  inadmissible, then Brent's method matches mass (7-5). No positive velocity
  floor is used. Exhausted profile iteration is a numerical failure; failure
  to bracket on the current iterate is not proof of a machine choke boundary.
- **Thermodynamics.** `H' = I + (r omega)^2 / 2` (7-37), `h = H' - W^2/2`
  (7-38), statics from `(h, s)`. The first gas model is a calorically perfect
  gas; the interface takes `(h, s)` so a variable-property model can follow.
- **Outer loop.** After every QN is solved, the stream surfaces are moved to
  their mass fractions (7-54 to 7-56) with Novak's damping (7-57, v11 `B* = 4`,
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
a forced vortex against its closed form (v9 is limited by the inlet-profile
interpolation, below 2e-7 relative error), a quadratic-swirl case at second
order, and in a lossless stage Euler work to 1e-8 J/kg, `H` and `s`
unchanged on every stream surface and the mass-averaged T0 across the stator
unchanged to 3e-10 K. In a curved annulus, the spherical source flow between
two cones with a common apex (exact, compressible, inlet Mach up to 0.71) is
matched at second order in the stream-surface spacing by the full model
(4.1e-4 at 11 surfaces, 2.6e-5 at 41, over every quasi-normal; the
quasi-normal spacing does not change it on these straight rays), with the
stream surfaces on the rays to 3e-6 degrees. There the linear model stays within 0.1% and the simple model
(no slope or curvature) is off by 8%, so the simple model is only for
near-cylindrical passages.

Mattingly example 9.1 (inputs as in turbo-design's example; no loss), 11
stream surfaces:

| | Pressure ratio | Polytropic efficiency | Inlet Mach |
|---|---:|---:|---:|
| this solver, full curvature | 1.29494 | 1.000000000000 | 0.718 |
| this solver, linear | 1.29628 | 1.000000000000 | 0.717 |
| this solver, simple | 1.30948 | 1.000000000000 | 0.708 |
| turbo-design, 1 streamline | 1.29856 | 1.00052 | 0.700 (imposed) |
| turbo-design, 11 streamlines | 1.31717 | 1.00518 | 0.700 (imposed) |

Averages are taken from the mass-averaged total enthalpy and entropy
(`averaged_total_state`), so a lossless machine has an efficiency of exactly
one. turbo-design imposes the inlet Mach number, where this solver derives it
from the mass flow and the annulus, so the two do not pose identical
problems; the comparison is an order-of-magnitude check, not a validation.

Open: with closely spaced quasi-normals Novak's damping (7-57) makes the
outer loop slow (292 iterations and about a minute for 25 quasi-normals and
41 surfaces, against 26 iterations for 7); a faster repositioning scheme is
worth having before large multistage cases.

Not yet: correlation rows, blockage models, the environment's simulator on
this solver.

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

## Start-up homotopy

A cold start (uniform-flow stream surfaces) can fail where a solution exists.
On the first outer iterations the stream surfaces are far from their final
positions; a row whose loss rises with its exit diffusion (Aungier's
off-design loss through `D_eq`) then sees a low exit velocity near a wall, its
loss grows, the velocity falls further, and the quasi-normal has no solution.
Stage 52 at 34.24 kg/s shows it: the stator hub loss climbs from 0.06 to 0.29
within the first outer iteration while the converged solution, reached from a
neighbouring point, has a hub loss of 0.13.

`Throughflow.solve` therefore solves from the cold start first and, only if
that fails or does not converge, again with the row losses scaled from 0 to 1
in steps of `HOMOTOPY_STEP` (0, 0.25, 0.5, 0.75, 1 when every step
converges), every step starting from the stream surfaces of the last converged
one. A step that fails is halved and retried, down to `HOMOTOPY_MIN_STEP`
(1/64), and the step grows back after each success; with no failed step the
sequence is the fixed one used before this was added, so no point that
converged then changes. The last step is the full model, so
its solution is the model's solution at that point; a point that converges
cold never reaches the fallback, and when the fallback fails the cold-start
outcome (error or unconverged solution) is returned unchanged. On the
validation cases (stages 35-38, 52, 53) every one of the 100 measured-flow
points that converged cold gives identical numbers, 17 more converge, and
none is lost.

## Spanwise mixing (optional, off)

`sm_throughflow.solver.mixing` adds Gallimore's (1986) turbulent-diffusion
model of spanwise mixing: between quasi-normals each stream surface receives
the entropy, total-enthalpy and angular-momentum changes of his equations
(2)-(4) with the shear stresses and dissipation of his appendices, turbulent
Prandtl and Schmidt numbers of one, zero shear and heat flux at the walls, and
a uniform mixing coefficient from Gallimore and Cumpsty's eq. (9)
(`correlations.spanwise_mixing`). Energy and angular momentum are conserved
to round-off. Aungier's method has no mixing (he smooths the loss instead,
section 9.2), so the model is off in every profile; the simulator switch
`SlcAungierSimulator.mixing_model = "gallimore"` enables it for experiments.
Within one stage its effect is small (the diffusion length over a stage is a
few millimetres at the level of eq. (9)); it did not change the convergence
of stages 52 and 53. Its place is the multistage cases, where Gallimore shows
the effect accumulating from stage to stage.

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

## v6 convergence and physical verification

The original v5 homotopy observations above describe that historical working copy.
In v6 the fallback algorithm is preserved, with complete attempt diagnostics.
All inner row, quasi-normal and endwall loops now reject exhausted iterations;
the outer test includes all coupled fields, blockage and optional mixing.
Final-state mass, Euler/energy and entropy checks are independent of the stopping
test. Local blade Reynolds corrections also change the physical results.

See [the current scope specification](throughflow_domain.md) for exact tolerances,
geometry restrictions, limiter semantics and remaining qualification work. The
[reliability plan](throughflow_reliability_plan.md) tracks acceptance separately
from implementation. Numerical verification does not enable the score.

## v7 coupled acceleration

V7 adds bounded, weighted Type-II Anderson acceleration of stream-surface
positions and blockage together. Novak's local damping remains the base step;
its B* is held fixed during accelerated iteration to avoid mixing histories of
continually changing maps. Non-admissible extrapolation uses the base step and
restarts history. A failed accelerated solve retries the original Novak scheme,
including its adaptive B* reduction, before the existing loss homotopy proceeds.
The actual undamped residual and all independent balance checks remain required.

The old close-grid slowdown noted above is resolved on the synthetic refinement
suite; see [the v7 report](phase1_refinement.md) for the data and limits of that
claim. The empirical closures have not been recalibrated by this change.
