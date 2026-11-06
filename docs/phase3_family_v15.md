# v15: equivalent-camber deviation and its limits

The simulator is `slc_aungier_experimental_v15`. This change repairs an
inconsistency in applying the NASA Lewis deviation rule to MCA blade rows.
It does **not** repair the Stage 35–38 efficiency ordering. Experimental
qualification and design-ranking qualification remain false; scores remain
disabled. No coefficients are fitted to those four machines.

## Source and derivation

[NASA TN D-7345](https://ntrs.nasa.gov/api/citations/19740009588/downloads/19740009588.pdf),
printed p. 18, defines the Carter rule using equivalent camber: the exit
angular momentum is preserved while transporting the exit to the inlet
radius and meridional velocity. Its BLADE listing makes this precise:
printed p. 144, lines 71–73, constructs B2EQ; printed p. 147, lines 224–230,
computes the equivalent camber and then the physical exit metal angle.
These pages were inspected as rendered images, not inferred from OCR alone.

Let q=m/sqrt(sigma), b=kappa2+delta, and Omega_s be shaft speed with the
solver-to-positive-camber sign. The independently conserved quantity is
absolute angular momentum. Inverting the original design-mode construction
for a blade with known metal angles gives:

```text
tan(b_eq) = (r2/r1)(Wm2/Wm1) tan(b) + Omega_s (r2^2-r1^2)/(r1 Wm1)
theta_eq = (kappa1-b_eq)/(1-q)
delta    = q theta_eq
F(b)     = (1-q)(b-kappa2) + q(b_eq-kappa1) = 0
```

The code's existing m(setting angle,a/c) and sigma are retained. This is
the inversion of the equivalent-camber relation, not a reproduction of the
entire NASA design program, which also has distinct incidence, three-
dimensional edge corrections and blade construction options.

For positive radii/meridional velocities and 0<=q<1, F is strictly increasing:
F'=1-q+q a sec²(b)/(1+(a tan(b)+c)²)>0. Metal angles must lie strictly
between -90 and 90 degrees. A bracket over that interval gives a unique root;
54 fixed bisections make the result deterministic. Outside this correlation
domain the row reports `outside_model_scope`, not a proven physical choke.
At equal meridional speed and radius, delta=q(kappa1-kappa2), recovering the
existing two-dimensional Carter rule. Units and rotation-sign conventions
are tested using explicit absolute-circulation transport.

## Assembly correction

Through v14 the model uses actual blade camber for Carter deviation and
adds Aungier's independent 10(1-Wm2/Wm1) term to the actual exit angle.
The reference loss triangle receives the uncorrected deviation. In v15,
the annular reference is recomputed whenever the exit velocity changes and
used by both the reference loss triangle and actual exit prediction.
It is deliberately outside the inlet-only cache.

The off-design extension retains Aungier's incidence slope:
delta_actual=delta_reference+slope*(i-i_star). This is an explicit hybrid
assumption, not a new experimental validation of MCA off-design deviation.
The separate 10(1-Wm2/Wm1) term is omitted only for this MCA branch, since
the annular inversion already supplies the radius/velocity response.
Inlet guide vanes retain their existing Howell branch. Other blade families,
shock geometry, pressure-defect integration, convergence tolerances and
experimental input tables are unchanged.

Diagnostics identify the active branch and report its reference-deviation
correction relative to the old planar value. Numerical convergence remains
distinct from correlation validity and from experimental accuracy.

## Attribution before adoption

Two immutable v14-source research campaigns tested the implicit closure.
The first changed both reference loss and actual deviation, and ran five
coupled anchors plus all 96 measured-state row cases and six sensitivities.
The second changed only the exit-deviation prediction in the 96 row cases,
leaving the reference loss triangle unchanged. Their prototype and
`release_evidence=false` labels remain explicit.

- Coupled prototype: `20261105T094647238537Z_slc_aungier_experimental_v14`.
- Deviation-only attribution: `20261105T094819176607Z_slc_aungier_experimental_v14`.

Correcting the reference loss triangle reduces predicted rotor losses at
these four anchors. Supplying measured meridional conditions still leaves
the measured and predicted aspect-ratio loss differences with opposite signs.
This rejects the hypothesis that the old velocity-deviation approximation
alone explains the family error. The coupled prototype preserves the Stage 53
result exactly because that machine does not use the MCA branch.

## Remaining physical closure and training scope

The fixed geometric passage-shock location, its interaction with profile and
endwall boundary layers, and the planar representation of the NASA conical
sections remain unresolved. TN D-7345's blade-construction equations define
constant local turning per path distance on a cone; projecting a planar
profile is not an exact implementation of that construction. A correction
must first reproduce source blade coordinates and independent limits before
being judged on the four development machines.

The rotor-exit states in the reports are reconstructed, and PHISS denotes an
assumed shock location. Neither supplies an independent measured shock foot.
Do not replace the general model with per-machine PHISS or efficiency offsets.
The four peak-flow anchors also vary operating flow and other geometry; their
differences are not isolated universal aspect-ratio derivatives.

For design-model training, converged results retain value as versioned
development data for equations and balance checks. They are still unsuitable
as trusted labels of the relative efficiency merit of these design changes.
Qualification requires source-checked geometry, a general transonic closure,
uncertainty assessment, and held-out machines under the unchanged gates.

## Matched v14/v15 experiment

The frozen **108 jobs**, **96 measured-state row closures** and **six wall/inlet
sensitivities** were repeated. Every design and task matches v14 except the
simulator version. The jobs include research projections, repeats, perturbations
and grids; they are not 108 independent experimental observations.

| Outcome | v14 | v15 |
|---|---:|---:|
| Converged, all jobs | 75/108 | 75/108 |
| Original inputs | 35/54 | 35/54 |
| Projected research inputs | 40/54 | 40/54 |
| Original experimental readings | 23/33 | 23/33 |
| Projected experimental readings | 28/33 | 28/33 |
| Previously converged jobs lost | — | 0 |

The successful job IDs are unchanged. The remaining outcomes are 20 unresolved
capacity limits, seven numerical failures, five unsupported inputs and one
invalid state. All 17 Stage 35–38 readings converge in both representations,
including Stage 35 at 90% speed. Both matched fourfold grids converge. Both
repeat anchors are bitwise identical, including station and row diagnostics.
No returned coupled solution activates supersonic compression clipping.

### Efficiency and family response

These original-annulus anchors are each at their own measured peak-flow
reading; the predicted optima were not searched or substituted.

| Stage | Measured eta (%) | v14 | v15 |
|---|---:|---:|---:|
| 35 | 84.5000 | 81.2996 | 81.4291 |
| 36 | 82.1000 | 81.7749 | 81.9867 |
| 37 | 84.0000 | 81.8093 | 81.9464 |
| 38 | 83.1000 | 82.3663 | 82.6104 |

| Difference, eta points | Measured | v14 | v15 |
|---|---:|---:|---:|
| 35→36 | -2.4000 | +0.4752 | +0.5576 |
| 37→38 | -0.9000 | +0.5570 | +0.6640 |
| 35→37 | -0.5000 | +0.5097 | +0.5174 |
| 36→38 | +1.0000 | +0.5914 | +0.6237 |

Both aspect-ratio signs remain reversed and move farther from measurement.
The 35→37 sign also remains wrong; 36→38 already had the correct sign in v14.
The projected interpretation has the same three wrong signs. Absolute eta
improvement must not be reported as a successful family-response correction.

![Matched efficiency comparison](../validation/campaigns/20261105T100759576915Z_slc_aungier_experimental_v15/family_efficiency.png)

### Broader error distribution

The following P90 absolute errors use the same successful experimental readings
in both versions. The original cohort has 23 readings, including Stage 53 in
both versions; it therefore differs from the 22-reading v13/v14 common cohort.

| Representation / paired readings | PR-rise relative error v14→v15 | Eta error (points) | Rotor TR-rise relative error |
|---|---:|---:|---:|
| original / 23 | 22.7909%→22.9991% | 3.9731→3.8722 | 14.9601%→16.4396% |
| projected / 28 | 21.6377%→22.3073% | 3.8299→3.7094 | 15.0996%→16.2548% |

Eta error decreases modestly; pressure-rise and temperature-rise errors worsen.
This is a source-consistency change, not a broad predictive-accuracy upgrade.

### Measured-state rotor closures

Equal-sample core means condition the closure on measured/reconstructed inlet
and exit states; they are not a coupled throughflow prediction or a mass-weighted
stage efficiency budget.

| Rotor | Reported loss | v14 loss | v15 loss | Reported deviation (deg) | v14 deviation | v15 deviation |
|---|---:|---:|---:|---:|---:|---:|
| 35 | 0.10820 | 0.15927 | 0.15774 | 4.740 | 5.538 | 5.548 |
| 36 | 0.13180 | 0.15543 | 0.15275 | 5.220 | 5.466 | 5.539 |
| 37 | 0.11860 | 0.18313 | 0.17845 | 8.100 | 7.619 | 7.647 |
| 38 | 0.14480 | 0.18204 | 0.17383 | 8.360 | 7.249 | 7.394 |

The absolute rotor loss overprediction decreases, but the low/high aspect-ratio
ordering remains wrong even when the meridional states are supplied. The new
reference triangle reduces loss more in the higher-aspect-ratio rotors; this
is consistent with the worsening coupled efficiency difference, but it is
not an additive decomposition. Full stator and rotor results are retained.

### Stage 53

Original Stage 53 at 100% speed/reading 2993 converges. Every performance metric
is bitwise identical to v14: stage PR=1.3301689232790066 and eta=0.8726614205804744
versus measured PR=1.329 and eta=0.879. Its DCA branch is unchanged. This verifies
preservation of v14's recovered solution, not additional empirical validation.

## Evidence locations

- [Matched numerical campaign](../validation/campaigns/20261105T095546195498Z_slc_aungier_experimental_v15/manifest.json).
- [Paired analysis and all family comparisons](../validation/campaigns/20261105T100759576915Z_slc_aungier_experimental_v15/summary.json).
- [Conditioned row means, including prototypes](../validation/campaigns/20261105T100759576915Z_slc_aungier_experimental_v15/row_anchors.json).

The numerical campaign archives the exact production source and its unchanged
v14 inputs. The final audit below separately captures completed tests and the
updated documentation; historical campaign files are not rewritten.

## Final frozen verification

The full suite passes **289 tests with one import-order skip** in
1510.73 seconds. The entry-point module passes all five tests in a
fresh process, including that skipped check: **290 distinct tests verified**.
This includes 18 new equivalent-camber tests, Stage 53 repeated convergence,
Stage 35 fine-grid/90% regressions, conservation and disabled-score checks.

The audit verifies 811 protected historical files, 114 v14 baseline JSON
artifacts, the frozen protocol and all v5–v14 golden assignments unchanged.
All 108 design/task pairs differ from v14 only by simulator version.
The simulation campaign and final production package are byte-identical.

Production SHA256: `fbc4d57167f594f98a92dd8765fb63913e4c7da35cfb2ccfc08a0f7a261eb719`.

[Frozen audit](../validation/campaigns/20261105T102341258925Z_slc_aungier_experimental_v15/manifest.json) includes
test logs, input hashes, original NASA source PDF and source archive.
The initial focused test run failed because its synthetic MCA fixture
omitted mandatory section-shape input; the corrected fixture and passing
reruns are retained. No failed run is represented as passed evidence.
