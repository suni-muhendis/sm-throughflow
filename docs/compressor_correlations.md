# Axial-compressor cascade correlations: source notes

`sm_throughflow.correlations.aungier` implements the empirical blade-row
performance models of R. H. Aungier, *Axial-Flow Compressors: A Strategy for
Aerodynamic Design and Analysis*, ASME Press, 2003, chapters 4 and 6. Every
function cites its equation. The equations were transcribed from the book's
pages, not from memory, and each is tested against the book's figures, where
Aungier plots his equations (circles) over the data they fit (lines, mostly
Johnsen and Bullock, NASA SP-36, 1965).

## Conventions (Aungier sections 4.1, 6.1)

- Angles in **degrees**, measured from the axial direction, as positive
  magnitudes in the cascade frame: the blade turns the flow from beta1 toward
  the smaller beta2. This is the frame of `sm_throughflow.correlations`
  (camber >= 0); a solver adapter flips signs for rows drawn the other way.
- kappa1, kappa2: blade (camberline) angles; theta = kappa1 - kappa2 camber
  (4-34, 6-6); gamma stagger; i = beta1 - kappa1 incidence (6-2);
  delta = beta2 - kappa2 deviation (6-3); alpha = beta1 - gamma angle of
  attack (6-1); sigma = c/s solidity (6-5); t_b/c maximum thickness ratio;
  a/c location of maximum camber.
- Circular-arc and NACA-65 equivalent circular-arc camberlines:
  chi1 = chi2 = theta/2, gamma = (kappa1 + kappa2)/2 (4-35, 4-36).
- NACA-65 lift coefficient and equivalent camber:
  tan(theta/4) = 0.05515 C_l0 / (a/c) (4-29, 6-7); with a/c = 0.5 this is
  tan(theta/4) = 0.1103 C_l0 (4-6).
- Profile shape factor K_sh: 1.0 NACA-65, 1.1 C.4, 0.7 double-circular-arc
  (section 6.2).
- Loss coefficient: omega = (P't1 - P't2) / (P't1 - P1), the solver's `inlet`
  basis.

## Throat opening (section 4.9)

Empirical, for NACA-65 blades (fitted to Dunavant et al. 1955 carpet plots),
also fair for C.4 parabolic-arc blades (Fig. 4-13):
phi = gamma (1 - 0.05 C_l0^1.5) + 5 C_l0^1.5 - 2 (4-30),
o/s = [(1 - (t_b/c) sqrt(sigma)) cos(phi)]^sqrt(sigma) (4-31).
Aungier prefers computed throats from the actual geometry, which
`correlations/blade_geometry.py` provides (section 4.9):

- Sections from Table 4-1: the NACA 65-010 and C.4 thickness distributions,
  laid normal to the camberline and along its length (section 4.1), with
  their leading- and trailing-edge circles (NACA 65: 0.687% chord at 10%
  thickness, scaled with the square of the thickness; C.4: 1.2% and 0.6%,
  proportional to it); camberlines: the NACA a = 1.0 mean line scaled by
  C_l0 from (4-6), the circular arc (4-7 to 4-10) and the parabolic arc
  (4-16 to 4-19, solved as a quadratic); the double circular arc
  (4-22 to 4-26) with its edge radius. On a parabolic-arc or NACA meanline
  the double-circular-arc profile is its thickness (that of the uncambered
  section, arcs tangent to the edge circles) laid normal to the camberline
  like the other profiles, with the edge circles on the camberline r0 from
  each end; on a circular-arc meanline it is the exact construction, and the
  two agree to 2e-3 chord there (tested).
- The section is staggered by gamma (4-32 to 4-36) and the throat is the
  minimum distance between the suction side of one blade and the pressure
  side and edge circles of the next, one pitch along.
- **Table 4-1 misprint**: the NACA 65-010 thickness at 2.5% chord reads
  3.480; NACA Report 824 gives the half-thickness 1.574 (recomputed 1.5748),
  so the value is 3.148. Every other station, the a = 1.0 mean line and the
  leading-edge radius agree with Report 824. The C.4 ordinates agree with an
  independent tabulation (Vinogradov, RUDN J. Eng. Res.).
- **Double circular arc, lower surface**: the book obtains it by giving t_b
  and r0 negative values in (4-22 to 4-26); taken literally that makes the
  lower arc tangent to the mirror image of the edge circle. The code makes
  both arcs tangent to the same edge circles, centred on the camberline r0
  from each end, as section 4.6 describes (tested).
- **Checks**: a flat plate gives o/s = cos(gamma). Against Aungier's own
  constructed NACA 65-series cascades (Fig. 4-12, sigma = 1, 60 points read
  at 300 dpi) the computed o/s differ by a median 0.001 and at most 0.004,
  the reading accuracy. Against his C.4 parabolic-arc cascades (Fig. 4-13,
  a/c = 0.4) they agree as closely up to 40 deg stagger; at 50 and 60 deg and
  low camber the figure is up to 0.019 wider. No single thickness explains
  the figure (40 deg needs 10%, 60 deg about 6%), and the figure puts the
  C.4 throat above the NACA 65 one at 60 deg although the C.4 is the blunter
  section; a plausible cause is Aungier's coarse search ("about 50 points"
  per surface), which can miss a blunt nose where it sets the throat. Those
  curves are not used as a reference.

## Design (minimum-loss) incidence (section 6.2)

Two models; Aungier reports consistently better performance predictions with
the first.

1. Design angle of attack, after Herrig et al. (1957):
   alpha* = [3.6 K_sh K_t,i + 0.3532 theta (a/c)^0.25] sigma^e (6-8),
   e = 0.65 - 0.002 theta (6-9), K_t,i = (10 t_b/c)^q (6-10),
   q = 0.28 / [0.1 + (t_b/c)^0.3] (6-11). Then i* = alpha* + gamma - kappa1
   (6-18).
2. Lieblein (1960) design incidence: i* = K_sh K_t,i (i0*)_10 + n theta
   (6-12), (i0*)_10 = beta1^p / [5 + 46 exp(-2.3 sigma)]
   - 0.1 sigma^3 exp[(beta1 - 70)/4] (6-13), p = 0.914 + sigma^3/160 (6-14),
   n = 0.025 sigma - 0.06 - (beta1/90)^(1 + 1.2 sigma) / (1.5 + 0.43 sigma)
   (6-15). beta1 is itself beta1 = kappa1 + i*, so this is iterated. For
   a/c != 0.5: pseudo inlet angle kappa1_bar = |gamma| + theta/2 (6-16),
   alpha* = kappa1_bar + i* - |gamma| + (a/c - 0.5) theta (6-17), then (6-18).

## Design deviation (section 6.3)

Lieblein: delta* = K_sh K_t,delta (delta0*)_10 + m theta (6-19),
(delta0*)_10 = 0.01 sigma beta1 + [0.74 sigma^1.9 + 3 sigma](beta1/90)^(1.67 + 1.09 sigma)
(6-20), m = m_1.0 / sigma^b (6-21), with x = beta1/100:
m_1.0 = 0.17 - 0.0333 x + 0.333 x^2 for NACA-65 (6-22),
m_1.0 = 0.249 + 0.074 x - 0.132 x^2 + 0.316 x^3 for circular-arc (6-23),
b = 0.9625 - 0.17 x - 0.85 x^3 (6-24),
K_t,delta = 6.25 (t_b/c) + 37.5 (t_b/c)^2 (6-25). beta1 is the design inlet
flow angle.

Modified Howell, for the A4K6 and parabolic-arc camberlines and for every
inlet guide vane: delta* = [0.92 (a/c)^2 + 0.002 kappa2] / (1 - 0.002 theta / sqrt(sigma))
* theta / sqrt(sigma) + (K_sh K_t,delta - 1)(delta0*)_10 (6-26).

## Design loss (section 6.4)

- Diffusion factor D = 1 - W2/W1 + (W_theta1 - W_theta2)/(2 sigma W1) (6-31);
  D-based design loss omega* cos(beta2*)/(2 sigma) = 0.0035 [1 + 3.5 D* + 37 D*^4]
  (6-34), diffusion limit D* = 0.6.
- Equivalent diffusion factor at design incidence:
  (W_max/W1)* = 1.12 + 0.61 cos^2(beta1*)/sigma [tan beta1* - tan beta2*]
  (6-35); D_eq* = (W_max/W1)* (cos beta2*/cos beta1*)(W_m1/W_m2) (6-36);
  omega* cos(beta2*)/(2 sigma) (W1*/W2*)^2 = 0.004 [1 + 3.1 (D_eq* - 1)^2 + 0.4 (D_eq* - 1)^8]
  (6-37), diffusion limit D_eq = 2.
- Off-design and annular forms of W_max/W1 (Klapproth, in Lieblein 1959):
  1.12 + 0.61 cos^2(beta1)/sigma [tan beta1 - tan beta2] + alpha (i - i*)^1.43 (6-38),
  1.12 + 0.61 cos^2(beta1)/sigma (r1 C_theta1 - r2 C_theta2)/(r1 C_m1) + alpha (i - i*)^1.43
  (6-39), the incidence term only for i > i*; alpha = 0.0117 NACA-65, 0.007 C.4.
  In (6-39) the swirl is absolute, taken in the cascade frame (sign flipped
  for a row drawn the other way); with r1 = r2 and C_m1 = C_m2 it reduces to
  (6-38). D_eq = (W_max/W1)(W1/W2) (6-30).
- **Aungier's choice** (section 6.11) is the general D_eq form
  omega* cos(beta2*)/(2 sigma) (W1*/W2*)^2 = K1 [K2 + 3.1 (D_eq* - 1)^2 + 0.4 (D_eq* - 1)^8]
  (6-46), with K1 = 0.0073 and K2 = 1 + (s/h) cos(beta2) (6-99), which adds
  end-wall loss through the pitch-to-height ratio. With a Reynolds-number
  correction, K2 = 1 + (s/h) cos(beta2) + 0.004 K_Re / K1 (6-100),
  K_Re = sqrt(2.5e5/Re_c) - 1 for Re_c < 2.5e5 (6-101),
  K_Re = [log(2.5e5)/log(Re_c)]^2.58 - 1 above (6-102). A simpler
  alternative he reports: K1 = 0.004, K2 = 4.
- Howell's end-wall and secondary drag (6-40 to 6-44) is described but not
  part of the chosen model.

## Stall incidence and Mach number (sections 6.5, 6.6)

- Stall angles of attack (Herrig et al. 1957), degrees:
  alpha_c - alpha* = -9 + [1 - (30/beta1c)^0.48] theta/4.176 (6-47),
  alpha_s - alpha* = 10.3 + [2.92 - beta1s/15.6] theta/8.2 (6-48);
  beta1c is limited to >= 20 deg (6-47 is singular at 0); beta1 = alpha + gamma
  makes both iterative.
- Ranges R_c = i* - i_c, R_s = i_s - i* (6-49, 6-50), reduced with the
  relative inlet Mach number M1':
  i_c = i* - R_c / [1 + 0.5 M1'^3] (6-51),
  i_s = i* + R_s / [1 + 0.5 (K_sh M1')^3] (6-52), K_sh limited to <= 1.
- Choke: rho1 W1 s cos(beta1,choke) = o rho* W* (6-53), and
  i_c >= beta1,choke - kappa1 + 1 deg (6-54).
- Minimum-loss incidence i_m = i_c + (i_s - i_c) R_c / (R_c + R_s) (6-55);
  omega_m = omega* [1 + (i_m - i*)^2 / R_s^2] (6-58).
- Critical Mach number M_c' = M1' W*/W_max (6-59), with W_max from (6-39) at
  i = i*, delta = delta*; above it
  omega_m = omega* [1 + (i_m - i*)^2 / R_s^2] + K_sh [(M'/M_c' - 1) W*/W1]^2
  (6-60), with M' <= 1 (the supersonic part is the shock loss below).

## Shock loss (section 6.7)

Aungier follows Swan (1961) and Miller, Lewis and Hartmann (1961), who both
build on F. C. Schwenk, G. W. Lewis and M. J. Hartmann, "A Preliminary
Analysis of the Magnitude of Shock Losses in Transonic Compressors", NACA RM
E57A30 (1957), appendix B (read on NTRS; the 1961 ASME papers are behind a
paywall). The model:

- Double-circular-arc blade with a sharp leading edge; the flow enters
  tangent to the suction surface, so beta1 = 90 - psi = theta_u/2 + gamma
  (6-67). Upper-surface camber tan(theta_u/4) = tan(theta/4) + t_b/c (6-65),
  psi = 90 - theta_u/2 - kappa1 + theta/2 (6-68).
- The passage shock runs from the adjacent leading edge normal to the suction
  surface; the surface turns by phi up to it,
  tan phi = s cos psi / (s sin psi + R_u) (6-69). The sign follows from the
  angle 90 - psi - phi marked in Fig. 6-17, and a direct construction in
  (axial, tangential) coordinates reproduces (6-69) to 1e-10 (test).
- Prandtl-Meyer expansion through phi from M1' to M_S' (6-70); the loss is
  that of a normal shock at a mean of M1' and M_S' (6-71), on the inlet basis
  omega_s = (1 - P'_b/P'_a) / (1 - P1/P'1) (NACA eq. B2). The method needs
  M1' >= 1; omega_s = 0 below.

Implemented for a perfect gas (closed-form nu(M) and normal-shock relations),
which is what our solver's `PerfectGas` needs; Aungier's numerical form
(6-70, 6-72 to 6-75) is the same physics for a general equation of state.
Tested against the NACA Rep. 1135 tables (nu(2) = 26.380 deg, P02/P01 at
M = 2 = 0.72087).

Three points differ from the book as printed:

- **(6-61) and (6-63) are misprinted.** They read 2R/c = sin(theta/2); the
  circular-arc relation the text cites, (4-7), is c/2 = R sin(theta/2). The
  code uses (4-7).
- **The mean in (6-71).** Aungier's text says the shock Mach number is "the
  average of the blade inlet Mach number and the expanded flow blade surface
  Mach number", but (6-71) prints sqrt(M1' M_S'). The NACA report says "the
  average of the end-point Mach numbers", and its worked values decide which:
  10 deg of supersonic turning at M1' = 1.0 gives omega_s "approximately
  0.02" and at M1' = 1.4 "approximately seven times" that. The arithmetic
  mean gives 0.0191 and 7.2 times; the geometric mean gives 0.0148 and 8.9
  times. The arithmetic mean is also the one Miller and Hartmann (NACA RM
  E58A14b, 1958) checked against measured passage-shock losses in a
  transonic rotor (0.190 to 0.192 predicted, 0.191 to 0.194 measured).
  `shock_loss` therefore defaults to `mean="arithmetic"`; `"geometric"` keeps
  Aungier's printed form.
- **phi <= theta_u.** At low solidity the line from the adjacent leading edge
  meets the suction-surface circle behind the trailing edge; phi is then
  limited to the turning of the whole surface. The book does not state this
  bound.

**Multiple-circular-arc sections.** NASA Lewis transonic blading (stages
35 to 38, rotor 67 and others) uses Crouse's multiple circular arc: J. E.
Crouse, D. C. Janetzke and R. E. Schwirian, NASA TN D-5437 (1969), and J. E.
Crouse, NASA TN D-7345 (1974), the "reference 4" of NASA TP-1337. The
meanline is two arcs whose angle falls at a constant rate along their path,
C1 on the front and C2 on the rear, tangent at the transition point (TN
D-7345 eqs. 1-4; its inputs c_t/c and C1/C2, printed pp. 4-9). Each surface
is two such arcs too (TN D-5437 eqs. 16-25, fig. 6): at the
maximum-thickness point the surfaces lie t/2 from the meanline along its
normal and parallel to it (eq. 24); the surface arc through that point is
fixed by it and by the edge on its side of the transition; the other arc
continues, tangent, from the normal through the meanline's transition point
to the other edge. The edges are circles centred on the meanline (TN
D-7345); the code lays the section out in the cascade plane, where the
reports use the developed blade-element cone. Checks: equal rates give the
circular arc (to 1e-9); on all eight rows of stages 35 to 38 the meanline,
with the transition point located from the printed ZTC, returns the printed
transition angle KTC within 0.14 deg and the setting angle within 0.18 deg;
the suction-surface angle at the leading edge exceeds the meanline's by 0.6
to 2 deg more than the printed DELTA INC, and the expansion angle below
exceeds the printed PHISS by 1 to 2 deg (the cone layout and the edge
treatment are the likely difference).

For incidence, deviation and loss the multiple circular arc is a
circular-arc section: K_sh = 0.7 as for the double circular arc, Lieblein's
circular-arc deviation (6-19), and a/c, where the correlations use it (the
design angle of attack, 6-8), is the chordwise position of the maximum
camber of the constructed meanline. The Lewis designers used Carter's rule
with m fitted to Carter and Hughes's curves as a function of setting angle
and a/c, on an equivalent-circulation camber (TN D-7345 eqs. 20-21; NASA TM
X-2379; GE CR-54581 app. B); it is a candidate for a later comparison.

**Expansion angle from the constructed section.** (6-65) to (6-69) take
the suction surface as a circular arc that turns through the whole camber.
That holds for a double circular arc and fails for the blades transonic rows
actually use: multiple-circular-arc and other aft-loaded sections keep the
surface ahead of the shock nearly straight, which is the point of their
design. On NASA Stage 35 the book's relation gives 10 to 17 deg where the
report prints a suction-surface camber ahead of the shock (PHISS) of 1.5 to
11 deg, and the shock loss came out about 1.5 times the designers'. For
double- and multiple-circular-arc profiles the simulator therefore reads phi
off the constructed cascade (`suction_surface_expansion_geometric`): the turning of
the suction surface from where it leaves the leading-edge circle to the foot
of the normal from the adjacent blade's leading edge, the same construction
on the actual surface. For a circular-arc meanline it reproduces (6-69) to
0.3 deg with a sharp edge (tested); on Stage 35's sections, with the
parabolic arc fitted to the printed setting angles, it is within 0.5 deg of
PHISS at the hub and 4 to 6 deg above it at the tip, where one a/c per row
cannot represent the nearly straight front of the MCA section. It is computed
once per row at the eleven design sections, like the throat. NACA 65 and
C.4 rows keep the book's relation: their rounded noses have no defined
start of the suction-surface turning.

Not modelled, as in Aungier: the bow-shock loss ahead of the leading edge
(small at the near-zero incidence of transonic rows, NACA RM E57A30) and
Swan's leading-edge radius in (6-69). The NACA report also lets the flow
arrive at an incidence to the suction surface (Delta nu = beta1' - xi_z,
eq. B1); Aungier fixes it tangent, and so do we.

## Off-design (section 6.8)

- Deviation slope at design incidence (Johnsen and Bullock):
  (d delta/d i)* = [1 + (sigma + 0.25 sigma^4)(beta1/53)^2.5] / exp(3.1 sigma) (6-76).
- delta = delta* + (d delta/d i)* (i - i*) + 10 (1 - W_m2/W_m1) (6-77); the
  incidence term is dropped for inlet guide vanes.
- xi = (i - i_m)/(i_s - i_m) for i >= i_m (6-78), (i - i_m)/(i_m - i_c) below
  (6-79); omega = omega_s + omega_m [1 + xi^2] for -2 <= xi <= 1 (6-80),
  omega_s + omega_m [5 - 4 (xi + 2)] for xi < -2 (6-81),
  omega_s + omega_m [2 + 2 (xi - 1)] for xi > 1 (6-82); omega_s is the shock loss.
- Wake blockage B_wake = 0 for D_eq <= 2, 1 - (2/D_eq)^0.9 above (6-83, 6-84),
  with D_eq at the off-design incidence and deviation.

## Clearance and seal leakage (sections 6.9, 6.10)

Tip clearance, from Aungier's centrifugal-impeller model (Aungier 1995, J.
Turbomach. 117; *Centrifugal Compressors*, 2000):

- tau = pi delta_c [(r rho C_m)_1 + (r rho C_m)_2][r2 C_theta2 - r1 C_theta1]
  (6-85), the torque on the flow through a band delta_c high at the gap;
  dP = tau / (Z r_tip delta_c c cos gamma) (6-86). delta_c cancels: dP is the
  blade loading at the gap. At constant r and r rho C_m it reduces to the
  cascade momentum balance dP c cos gamma = rho C_m s dC_theta (test).
- U_c = 0.816 sqrt(2 dP / rho_bar) / N_row^0.2 (6-87); m_c = rho_bar U_c Z
  delta_c c cos gamma (6-88); dP_t = dP m_c / m (6-89), the row's
  mass-averaged total-pressure loss. The 0.816 of the centrifugal model could
  not be read at its source (paywalled); two independent open codes that
  implement Aungier's models use the same constant (the CCMD centrifugal code,
  `Ucl = 0.816*SQRT(2*Pcl/rho2)`, and an axial code with the / N_row^0.2
  form). N_row^0.2 is Aungier's own multistage calibration.
- Spanwise distribution: linear across the annulus, zero at the wall
  opposite the gap, with the integral equal to (6-89); Aungier does this
  because a through-flow analysis without spanwise mixing would otherwise pile
  the loss up on the endwall stream surfaces and diverge. The book does not
  name the spanwise coordinate; since (6-89) is a mass-flow average we use the
  mass fraction, so the multiplier is 2x with x the mass fraction from the far
  wall (`leakage_loss_distribution`).

Shroud seal leakage (stator shrouds), Egli (1935) with Aungier's (2000) fits:

- dP_t = dP m_leak / m (6-90), distributed like the clearance loss;
  m_leak = 2 pi r_seal delta_c C_t C_c C_r rho sqrt(R T) (6-91), rho and T on
  the high-pressure side; C_r (6-92); C_c (6-94 to 6-96), for N <= 12 and
  delta_c/p <= X2 - 1, where it peaks.
- **(6-93) is misprinted.** The book prints
  C_t = [2.143 ln(N) - 1.464] / (N - 4.322) [1 - P_R]^(0.375 P_R), which is
  negative for N <= 4 and singular at N = 4.322. The intended form is
  C_t = 2.143 [ln(N) - 1.464] / (N - 4.322) ..., whose numerator vanishes
  where the denominator does (ln 4.322 = 1.4637). Checked against Martin's
  ideal labyrinth, sqrt[(1 - P_R^2) / (N - ln P_R)]: the bracketed form is
  1.02 to 1.28 times it over N = 2 to 12, P_R = 0.3 to 0.9, closing in as N
  grows (a real labyrinth leaks more than the ideal one); the printed form is
  negative or 1.8 to 3.8 times it. The original fit (Aungier 2000) was not
  available to confirm the bracket directly.

Not reproduced: Aungier's extension of C_c beyond 12 fins (in his 2000 book),
and the end-wall boundary-layer corrections for seal leakage (section 8.6),
which belong to his end-wall model.

## Verification against the book's figures

The circle markers of figures 6-2 to 6-18 were located on 300 dpi renders of
the pages by ring-template matching, with the axes calibrated from the frame
tick marks, and are kept in `tests/fixtures/aungier_2003_figures.json`.
`tests/test_correlations_aungier.py` compares each equation with them:

| Figure | Equation | Circles | Median, max |equation - figure| | Axis span |
|---|---|---:|---|---|
| 6-2 | design angle of attack (6-8 to 6-11, 4-6) | 61 | 0.021, 0.24 deg | 32 deg |
| 6-3 | K_t,i (6-10), against Johnsen and Bullock's data | 29 | 0.020, 0.072 | 1.3 |
| 6-4 | (i0*)_10 (6-13, 6-14) | 47 | 0.013, 0.099 deg | 12 deg |
| 6-5 | n (6-15) | 46 | 0.0004, 0.005 | 0.5 |
| 6-6 | (delta0*)_10 (6-20) | 24 | 0.010, 0.017 deg | 5.5 deg |
| 6-7 | m_1.0 (6-22, 6-23) | 17 | 0.0002, 0.0003 | 0.3 |
| 6-8 | b (6-24) | 12 | 0.0004, 0.0009 | 0.5 |
| 6-9 | K_t,delta (6-25) | 15 | 0.005, 0.007 | 1.4 |
| 6-11 | D-based design loss (6-34) | 17 | 7e-5, 1.2e-4 | 0.03 |
| 6-12 | D_eq-based design loss (6-37) | 7 | 1.3e-4, 2.7e-4 | 0.06 |
| 6-14 | stall angles of attack (6-47, 6-48) | 64 | 0.012, 0.61 deg | 26 deg |
| 6-18 | off-design deviation slope (6-76) | 69 | 0.001, 0.034 | 1 |

The medians are at the resolution of the reading, so the equations are
transcribed as printed. The maxima come from circles that touch a line end, a
label or each other (the 65-(27)10 end points in 6-2, the crowded low-camber
region of 6-14). The book's statement that (4-29) gives 33.5 deg at C_l0 = 1
for the A4K6 camberline is reproduced.

## Open points

- **Howell's secondary drag coefficient: the book's (6-43) is a misprint.**
  The page reads C_Ds = 0.18 C_L^2 (checked at 250 dpi). The value used in
  the literature is 0.018 C_L^2, for example Y_sec = 0.018 sigma cos^2(beta1)
  / cos^3(beta_m) C_L^2 attributed to Howell; that source could not be opened
  (publisher 403), and Howell (1945, Proc. IMechE 153) is not openly
  available. The physics settles it: for a typical mid-span blade
  (beta1 = 50, beta2 = 25 deg, sigma = 1, s/h = 0.5; C_L = 1.12), with the
  profile loss of (6-34) and the annulus drag of (6-42), 0.018 gives a
  secondary loss of 0.020 and a total of 0.073, a normal row loss with the
  profile loss 60% of it; 0.18 gives a secondary loss of 0.20 and a total of
  0.26, with the profile loss 17% of it, which no working compressor shows.
  Howell's own split (profile loss 39% of the total at design, as quoted in
  NASA CR-3671) is of the first kind. (6-43) is not used by the implemented
  model; if it is ever used, the coefficient is 0.018.
- **Carter's rule, confirmed at the source.** A. D. S. Carter, "The Low
  Speed Performance of Related Aerofoils in Cascades", ARC C.P. No. 29
  (1950), eq. (6): delta = m theta sqrt(s/c) for compressor cascades and
  delta = m theta s/c for turbine cascades, with m a function of the position
  of maximum camber and the stagger (his Fig. 6). Howell's fit
  m = 0.23 (2a/c)^2 + kappa2/500 equals the leading term of Aungier's (6-26),
  0.92 (a/c)^2 + 0.002 kappa2, which confirms that equation independently.
- Aungier calibrates K1, K2, the deviation and the off-design loss against his
  own through-flow analysis and end-wall boundary-layer model (chapters 7, 8);
  he warns that the parts "cannot really be separated from the whole". Our
  results are his models inside our solver, and need their own validation.
