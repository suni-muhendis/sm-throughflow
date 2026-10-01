# End-wall boundary layers and blockage

`sm_throughflow.solver.endwall.EndwallBoundaryLayers` is Aungier's end-wall
boundary-layer analysis (*Axial-Flow Compressors*, 2003, chapter 8). Aungier
uses it to predict end-wall blockage only, not end-wall loss, which his row
model covers through K2 (6-99) and the leakage losses; his K1 = 0.0073 and his
off-design loss model were calibrated with it in place. Pass it to
`Throughflow(endwall=...)`; the solution then carries the blockage factor of
every quasi-normal (`solution.blockage`) and the boundary-layer data
(`solution.endwall`).

## Equations (pages 181 to 195 of the book, read from the page images)

Velocities relative to the wall (V), the blade (W) and absolute (C):
C_m = W_m = V_m, C_theta = W_theta + r omega = V_theta + r omega_w (8-3, 8-4).
Pitch-averaged momentum-integral equations along each wall:

- mass and entrainment, d/dm[r rho V_me (delta - delta1*)] = r rho V_e E (8-5);
- meridional momentum (8-6), with the curvature term
  rho V_theta,e sin(phi) [V_theta,e (delta2* + theta22) + 2 omega_w r delta2*] and
  the blade-force defect r f_me nu;
- tangential momentum in the combined form (8-10),
  d/dm[r^2 rho V_me V_theta,e theta12] + r^2 delta1* f_theta,e = r^2 [tau_theta,w + f_theta,e nu],
  with the edge blade forces (8-8, 8-9).

Closure:

- Power-law profiles V_m/V_me = (y/delta)^n, V_theta/V_theta,e = (y/delta)^m
  (8-18 to 8-26), extended for m < 0.05 by (8-28 to 8-32) so that excess
  tangential momentum (H2 < 1) can be carried.
- Streamwise delta* and theta (8-37 to 8-41), Ludwieg-Tillmann skin friction
  (8-36) and wall shear along the edge streamline (8-33 to 8-35).
- Entrainment E = 0.025 (H - 1) (8-43), H the streamwise shape factor, as
  Aungier uses across blade rows.
- Blade-force defect nu_m = nu_theta = nu (Balsa and Mellor):
  nu0 = (0.12 g + delta_c/2) x^3/(1 + x^3), x = 8 theta11_bar/g (8-44),
  g = s cos(gamma) (8-2), plus the collateral-flow correction (8-45 to 8-57)
  with F (8-55), updated on every pass by (8-57).
- Limits: H, H1, H2 <= 2.4 (separation); Re_theta11 >= 250 (8-73); every
  defect thickness >= 0 in (8-40, 8-41); theta12 <= 0.99 delta/(n + 1).
- Shroud-seal leakage enters and leaves the boundary layer at the row inlet
  and exit (8-58 to 8-66), with the leakage mass flow from the row model
  (6-91), positive from the row's discharge to its inlet.
- Jump conditions (8-67 to 8-71): C_theta,e theta12 and the combinations in
  (8-70, 8-71) do not depend on the wall's frame, so the march carries
  r^2 rho V_me C_theta,e theta12 and needs no logic where the wall changes
  from rotating to stationary.
- Start (section 8.8): the inlet blockage B (default 0.02, Aungier's value for
  a start just ahead of the first row) split equally between the walls (8-72),
  H1 = 1.4 and m = 1/7.
- Blockage B = sum over both walls of 2 pi r rho V_me delta1* / m_dot (8-76),
  K_B = 1 - B (8-77).

## Checks

Every closure relation was re-derived from the stated profiles before coding;
`tests/test_endwall.py` checks them by quadrature:

- (8-20) to (8-26), (8-29) and (8-31) are exact consequences of the profiles.
- (8-40, 8-41) follow exactly from projecting the two profiles on the edge
  direction.
- (8-36) is the usual 0.246 x 10^(-0.678 H) Re_theta^-0.268 (1.561 is
  0.678 ln 10 rounded).
- (8-44) reproduces the curve of Fig. 8-6.
- **(8-30) is a fit, not the integral.** The extended profile (8-28) gives
  theta22/delta = -0.00044 + 0.9502 m - 1.5126 m^2; the book has
  0.95 m - 1.684 m^2, the exact slope with the intercept dropped and the
  quadratic chosen to keep continuity with the power law at m = 0.05
  ((0.0475 - 0.04329)/0.0025 = 1.684). It is within 0.5% near m = 0 and 6% at
  m = -0.8. The book's form is kept, since Aungier calibrated with it.
- A long annular duct with uniform flow behaves as a turbulent flat plate:
  after 2 m (Re_x = 5e6) theta11 is 11% below the 1/7-power law
  0.036 x Re_x^-0.2 with H1 = 1.38. Ludwieg-Tillmann gives a c_f about 7%
  below the flat-plate value at this Reynolds number, and the blockage itself
  accelerates the core slightly.
- On a subsonic free-vortex stage with B = 0.02 at the inlet the blockage
  reaches 0.0375 behind the stator; the NACA 10-stage compressor in Fig. 8-9
  (also started at 0.02) shows a similar rise over its first stages.

## Choices the book leaves open

- **Wall rotation.** Aungier asks for the first and last quasi-normal of the
  rotating hub. The default here is a drum turning at the rotor speed from
  the first rotor's inlet to the last rotor's exit, except under stators with
  a hub shroud seal; the shroud is stationary. `hub_speed` and
  `shroud_speed` override it per gap.
- **Viscosity**: Sutherland's law for air (mu = 1.716e-5 Pa s at 273.15 K,
  S = 110.4 K).
- **Discretization**: each gap between quasi-normals is one step; the
  equations are integrated with the trapezoidal rule, iterated to convergence
  on theta11, H1 and nu (section 8.8, steps 2 to 6). The blade forces in a
  row's gap are the gap averages from the edge flow, and nu acts only in
  blade-row gaps.
- **No tangential edge velocity.** Where V_theta,e = 0 in the wall's frame
  theta12 is undefined; the tangential profile keeps its previous m and the
  frame-free C_theta,e theta12 is carried on unchanged.
- **Coupling.** The boundary layers are recomputed after every outer
  iteration of the throughflow solution and K_B is under-relaxed by 0.5,
  with B limited to 0.5 (Aungier: "some limits and numerical damping are
  normally required"); convergence also requires K_B to settle.
- **Deep negative m.** Downstream of a stator that removes nearly all swirl,
  V_theta,e is small, theta12 = C_theta,e theta12 / V_theta,e is large and the
  extended profile goes to strongly negative m (H2 near 0.1). The book gives
  no lower limit and none is imposed; the products that enter the equations
  stay finite.
