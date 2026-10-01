# Aungier compressor blade-row model

`sm_throughflow.solver.aungier_row.AungierCompressorRow` applies the cascade
correlations of Aungier (2003), chapter 6, on every stream surface of the
streamline-curvature solver, with the performance-analysis practice of his
section 9.1 and 9.2. The correlations themselves are documented in
[compressor_correlations.md](compressor_correlations.md); this page records how
they are assembled and the choices the book leaves open.

## Input

Per row: blade count Z, speed omega (equal to the `BladeRow`'s), profile
(`naca65`, `c4`, `dca`: K_sh and the W_max incidence coefficient), camberline
(`naca65`, `circular_arc`, `parabolic_arc` with a/c), row number counted from
the inlet, inlet-guide-vane flag, and either a tip clearance (gap, wall) or a
shroud seal (radius, clearance, fins, fin pitch and thickness). Optionally the
throat opening o/s, the gas viscosity for the Reynolds correction, K1 and the
loss limit.

Per section, on cylinders hub to tip (section 9.1): radius, blade angles
kappa1, kappa2 from the axial direction (positive toward rotation, the
solver's sign), chord and t_b/c. The sections must cover the stream surfaces'
radii at the row inlet and exit.

## Order of evaluation on each stream surface

1. **Geometry on the stream surface** (9-1 to 9-6): tan phi = (r2 - r1)/(z2 - z1);
   chord c/cos phi, t_b/c cos phi, tan kappa -> cos phi tan kappa, with kappa1
   taken at r1, kappa2 at r2, chord and thickness at the mean radius;
   s = pi (r1 + r2)/Z. The stream surfaces move radially even in a
   cylindrical annulus, so the projection is always applied.
2. **Cascade frame**: the row's sign is that of mean(kappa1 - kappa2); every
   angle is multiplied by it so that camber is positive
   (correlations/__init__.py). Stagger from kappa1 = gamma + chi1 (4-32), chi1
   from (4-17 to 4-19), which is theta/2 for a circular arc.
3. **Inlet relative flow**: beta1, W1, M1', P't1 from the inlet station in
   the row's frame; sonic state rho* W* from the inlet relative total state
   (perfect gas: T* = 2 T't / (gamma + 1)).
4. **Design incidence** from the design angle of attack (6-8 to 6-11, 6-18),
   Aungier's preferred model. **Design deviation**: Lieblein (6-19 to 6-25)
   for NACA-65 and circular-arc camberlines, at the design inlet angle
   kappa1 + i*; modified Howell (6-26) for parabolic arcs and every inlet
   guide vane.
5. **Design loss** (6-46) with K1 = 0.0073 and K2 = 1 + (s/h) cos beta2* +
   0.004 K_Re / K1 (6-99, 6-100), h the mean annulus height of the row, K_Re
   zero unless a viscosity is given. D_eq* from Klapproth's annular W_max/W1
   (6-39) at the design angles beta1* = kappa1 + i*, beta2* = kappa2 + delta*
   and the actual meridional velocities and radii.
6. **Incidence range**: stall angles of attack (6-47, 6-48, iterated with
   beta1 = alpha + gamma), ranges R_c, R_s (6-49, 6-50), narrowed by M1'
   (6-51, 6-52); i_c limited by choke, i_c >= beta1,choke - kappa1 + 1 deg
   (6-53, 6-54), with o/s from (4-30, 4-31) unless given; i_m (6-55).
7. **Minimum loss** (6-58), with the supercritical term of (6-60) above
   M_c' = M1' W*/W_max (6-59), W_max from (6-39) at i*, delta*.
8. **Shock loss** omega_s (section 6.7, arithmetic mean by default).
9. **Off-design loss** (6-78 to 6-82) and **deviation** (6-76, 6-77) at the
   actual incidence, with W_m2/W_m1 from the current exit flow; no incidence
   term for inlet guide vanes.
10. **Wake blockage** B_wake (6-83, 6-84) from D_eq at the actual incidence and
    exit angle (6-39 with the incidence term for i > i*); the solver takes
    K_W = 1 - B_wake into the mass integral of the exit quasi-normal on each
    stream surface (7-5, 7-6, 7-54).
11. **Leakage**: clearance (6-85 to 6-89) from the gap-wall stream surface
    values, or shroud seal (6-90 to 6-96) from the static pressures across the
    row at the seal wall, with rho and T on the high-pressure side; both as
    total-pressure losses spread linearly in mass fraction from zero at the far
    wall.
12. **Limit and smoothing**: omega <= 0.5 (9-7), then the three-point
    smoothing of Delta P't = omega (P't1 - P1) across the span (9-8 to 9-11).

The row reports the exit flow angle, the loss on the inlet basis and the wake
blockage; `RowPerformance.diagnostics` carries every intermediate quantity per
stream surface, including Aungier's blade-row stall criterion: the equivalent
velocity ratio W_RE (9-16) and its stall limit (9-17 to 9-19).

## Choices the book leaves open

- **Lieblein's zero-camber deviation for negative inlet angles.** (6-20) is
  fitted for beta1 >= 0 and is not defined below (a fractional power of a
  negative number). A symmetric section at -beta1 deviates by the opposite
  amount, so the model uses sign(beta1) (delta0*)_10(|beta1|), and |beta1| in
  Lieblein's slope m (6-21) and in (6-76). This matters for inlet guide vanes
  (axial inflow, beta1 near zero) and for stators with little inlet swirl.
- **W_max incidence coefficient for double-circular-arc blades.** (6-38)
  gives 0.0117 for NACA-65 and 0.007 for C.4 circular-arc blades; DCA blades,
  also circular-arc, take 0.007.
- **Throat opening.** Aungier prefers throats computed from the constructed
  blade (chapter 4); without a given o/s the model uses his empirical
  (4-30, 4-31), which he fits to NACA-65 and finds fair for C.4 blades.
- **Seal pressure difference.** Section 6.10 takes "the pressure difference
  across the blade row"; the model uses the static pressures on the seal-wall
  stream surface at the row's inlet and exit.
- **The shroud end of the smoothing, (9-11), is misprinted** with index N - 3;
  the symmetric N - 2 is the form that keeps the trapezoidal integral over the
  two wall stream sheets, as the book says both end formulas do (test).

## Solver coupling

The model needs the exit flow (W_m2/W_m1 in the deviation, the exit state in
the design loss and leakage). The solver iterates each row's exit station
with the model, under-relaxing the model's angle, loss and wake blockage by
0.5 after the first pass; without it the deviation and W_m2 overshoot each
other (a factor of about -0.9 per pass, settling into a two-cycle). The inner
tolerance follows the outer iteration (1e-2 of its last change, between 1e-12
and 1e-6), so the converged solution is as sharp as before while early outer
iterations stay cheap. The part of the model that depends only on the blade
and the inlet flow is computed once per inlet station.

## Known properties

- **The shock loss switches on at M1' = 1 with a finite value**, as in the
  NACA model it comes from (which is restricted to M1' >= 1): at M1' = 1 the
  flow still expands by phi before the passage shock. A stream surface whose
  M1' crosses 1 between iterations sees its loss jump. Nothing is smoothed;
  validation will show whether this disturbs convergence on real transonic
  rotors.
- **Low solidity at a transonic tip** puts the passage-shock line behind the
  trailing edge; phi is then the whole suction-surface turning theta_u, and the
  shock loss is large (0.1 at M1' = 1.02 for sigma = 0.57, theta = 8 deg,
  t_b/c = 0.05).
- Aungier calibrated K1 = 0.0073 and the off-design loss model together with
  his end-wall boundary-layer analysis (chapter 8), which sets the end-wall
  blockage K_B: run the row model with `Throughflow(endwall=...)`, see
  [endwall_boundary_layer.md](endwall_boundary_layer.md).
