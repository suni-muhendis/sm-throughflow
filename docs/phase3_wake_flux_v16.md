# Shock loss budget and conservative wake reference

The new research work establishes a loss-budget gate for the shock model
and a downstream reduction for a prescribed wake. Stage 35–38 efficiency
ordering remains open. The reduction requires a profile from experiment
or a future blade-passage calculation.

## Literature and experimental inputs

- Youngren's MISES report, GTL 203, describes a coupled quasi-three-dimensional
  Euler and integral boundary-layer method that includes streamtube thickness,
  radius and rotation. It provides the architecture for solving blade
  pressure and displacement together. [MIT report](https://dspace.mit.edu/entities/publication/ee80c63a-ee82-4df2-8dfe-649532aafc21)
- Drela and Giles develop the displacement, momentum and kinetic energy
  quantities for a compressible integral layer and emphasize transition and
  separated flow. They motivate keeping more than one wake moment.
  [Drela and Giles](https://ora.ox.ac.uk/objects/uuid%3Aa42bfb7c-99bc-4f9f-b086-1bdee3d240ad)
- The DLR TEAMAero cascade paper reports surface pressure, outlet wake loss
  and turning, and compares conditions at different axial velocity density
  ratios. The accompanying open archive supplies blade coordinates and
  design-point PIV and shadowgraph data. The published wake curves and the
  raw optical archive have different coverage. An independent quantitative
  check needs matching run IDs, pressure references and survey planes.
  [Experiment](https://elib.dlr.de/195487/1/ETC2023-228.pdf) and
  [data inventory](https://doi.org/10.5281/zenodo.15380684)
- Amecke and Safarik use mass, momentum and energy to reduce a plane-cascade
  traverse to a mixed state. Lieblein and Roudebush distinguish loss on the
  survey plane from fully mixed loss in the low-speed limit.
  [DLR-FB 95-32](https://elib.dlr.de/37399/) and
  [NACA TN-3662](https://ntrs.nasa.gov/citations/19930084888)

## Measured-state gate for the current shock candidates

At the four original Stage 35–38 anchors, the measured inlet and exit
states give a reconstructed total row loss with the inlet relative head
as denominator and ideal exit pressure evaluated at conserved rothalpy.
The screen uses the larger of that reconstruction and the printed loss.
This is a conservative comparison rule, with no statistical uncertainty
claim. It omits the extrapolated wall points. The core subset spans 15–85%
from the tip. The shock terms retain the pressure-loss basis of their
respective v16 and nodewise research row models.
The integrated term uses v16's cell representation, while the pointwise
term has the local sample support. Both are listed to keep this distinction.

| Shock term | Exceeds total, all 36 sections | Exceeds total, 20 core sections |
|---|---:|---:|
| v16 pointwise | 1 | 1 |
| v16 integrated | 1 | 1 |
| Earlier passage-shock extension | 29 | 18 |

All 24 measured sections evaluated on the passage model's two choked
interpolation branches exceed the total. Five of its 12 unchoked points
also exceed it. At 30% span from tip on Stage 37, reading 4182, the
passage model gives 0.47138, the screened total is 0.14601 and the
integrated v16 shock term is 0.11920. A positive separation loss cannot
repair the fixed shock budget there. An interacted solution could still
move or weaken the shock. The result applies to this constructed-contour
extension in an annular rotor comparison. It leaves the source model's
published plane-cascade domain and the uncertain measured loss split
as separate questions.

[Measured-state screen](../validation/campaigns/20261105T152138646669Z_slc_aungier_experimental_v16/analysis.json)

## Conservative wake reduction

The reference accepts cell widths, static pressure, temperature, and normal
and tangential velocity on a constant-area plane spanning a full pitch.
It uses a single frame, a calorically perfect gas, no heat or shaft work,
and no Reynolds-stress flux terms. The blockage is the mass deficit
relative to an explicitly supplied edge mass flux on that plane.

The mixed state preserves area-averaged mass flux and normal momentum
flux, and mass-averaged tangential velocity and total enthalpy. With
normal momentum flux F, mass flux j and mixed tangential velocity v,
the normal velocity u satisfies

    (gamma + 1)/(2 gamma) u² - (F/j) u + R (Tt - v²/(2 cp)) = 0.

The reference selects the subsonic normal-flow root and checks entropy
production. It reports both the mass-averaged survey total pressure and
the total pressure of the uniform mixed state. A profile with reverse or
sonic normal flow lies outside its scope. The v16 wake blockage is an
effective area correction and has no measured traverse profile attached.
Direct comparison requires matching definitions and locations.

The reverse-flow exclusion matters in a cascade. CR-185118 Volume I,
printed p. 41 describes negative mean velocity in the near wake at
positive incidence. The low-speed far-wake comparison below has positive
throughflow and uses a different operating point and plane.

## First check with a measured wake

NASA CR-185118 supplies the low-speed DCA velocity traverse at 152.6% chord
and -8.5 degrees incidence. The 81 measured speeds are preserved verbatim.
The calculation uses a constant static pressure, a common 300 K total
temperature, the volume I reference density, a plane approximately normal
to the outlet flow, and fills the unsurveyed part of one projected pitch
with the edge state. It varies the edge estimate over 5, 10 and 15 samples
at each end. The spread covers that edge choice alone.

| Quantity | Result |
|---|---:|
| Mass deficit over a pitch | 2.248–2.269% |
| Edge-to-survey total-pressure deficit / inlet head | 0.01853–0.01875 |
| Additional pressure deficit through complete mixing / inlet head | 0.00140 |
| Edge-to-mixed total-pressure deficit / inlet head | 0.01993–0.02016 |
| Low-speed relation printed in CR-185118, applied to the same samples | 0.01898–0.01920 |

The authors report 0.018 from their velocity reduction at that plane and
0.028 from the measured passage-averaged pressure loss. The latter remains
distinct. The small gap between the authors' reduction and ours is retained.
Different edge definitions and quadrature can change the result. The comparison
checks a low-speed reduction with a supplied profile. It does not predict
the wake or establish the transonic model's accuracy.

[Source data and assumptions](../validation/cases/nasa_dca_cascade_wake/notes.md) and
[calculation record](../validation/campaigns/20261105T152815821410Z_slc_aungier_experimental_v16/analysis.json)

The next modelling gate is a matched cascade case with independently
specified geometry and streamtube contraction, surface pressure through
the shock, and downstream wake evidence. Solve the inviscid surface loading
and blade-layer displacement together and pass the same exit profile to
the loss and blockage reduction. Check the shock position and loss budget
before moving to coupled compressor runs. Keep local viscous dissipation,
shock entropy and downstream mixing on distinct accounting planes.

Use the TEAMAero study's TN 125 as the first transonic development target
and TN 112 as a higher-incidence test. Table 2 gives inlet Mach 1.21 and
1.19, and AVDR 1.047 and 1.074, respectively. Figures 5 and 7 show the
surface and outlet comparisons. For TN 125 the authors describe a shock
near 30% chord and a separation bubble extending to about 45%. Use these
as approximate features of the measured flow and retain the reported
unsteadiness when setting validation tolerances. The optical archive
listing only establishes coverage for its own three design-point runs.
[TEAMAero operating points and survey comparisons](https://elib.dlr.de/195487/1/ETC2023-228.pdf)

The optical archive index, geometry, run metadata and license were
retrieved with bounded HTTP ranges (under 80 kB transferred). ZIP entry
CRCs match the directory. The geometry has 420 rows, a closed planar
contour and a maximum point separation of 100.002 mm. Run IDs 37, 46
and 48 correspond to test numbers 234, 244 and 247, respectively, and
cover the shock foot, leading edge and trailing edge. Their inlet Mach
numbers are 1.20, 1.19 and 1.20. These are distinct from TN 125 and TN 112.
The archive supplies a CC BY-NC-ND 4.0 license. Its original geometry
and metadata remain local research inputs in `tmp/tcta_metadata`.
The coordinate file SHA-256 is
`68effcc971c6dbd8633ad4dc999e5f858ffed6484c106651fd35c1b72f02de48`.
[TEAMAero data archive](https://doi.org/10.5281/zenodo.15380684)

Reproduce the two comparisons with
`python -m validation.shock_loss_budget` and
`python -m validation.probe_wake_flux`.

The targeted run passed 22 tests, including six new wake tests, the
13 previous candidate checks, both Stage 35 eightfold grids and the
repeated Stage 53 regression. The three wake reductions repeated
exactly in a fresh process. The package source and runtime identity
match the frozen v16 baseline.
