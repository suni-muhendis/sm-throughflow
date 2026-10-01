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
Aungier prefers computed throats from the actual geometry.

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
  (6-60), with M' <= 1 (bow shocks are the next model).

## Shock loss (section 6.7)

Swan (1961): the flow enters tangent to the suction surface, expands along it
by a Prandtl-Meyer turn phi (6-61 to 6-70), and the loss is that of a normal
shock at M_in' = sqrt(M1' M_S') (6-71), from conservation across the shock
(6-72 to 6-75).

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

Tip clearance (from the centrifugal model of Aungier 2000):
tau = pi delta_c [(r rho C_m)_1 + (r rho C_m)_2][r2 C_theta2 - r1 C_theta1] (6-85),
dP = tau / (Z r_tip delta_c c cos gamma) (6-86),
U_c = 0.816 sqrt(2 dP / rho_bar) / N_row^0.2 (6-87),
m_c = rho_bar U_c Z delta_c c cos gamma (6-88), dP_t = dP m_c / m (6-89),
imposed as a total-pressure loss varying linearly across the annulus from zero
at the wall opposite the gap, with the integral equal to (6-89). Shroud seal
leakage by Egli (1935): (6-90) to (6-96).

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
