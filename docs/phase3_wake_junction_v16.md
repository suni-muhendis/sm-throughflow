# Trailing-edge junction and free-wake momentum

This research comparison uses a parallel, incompressible wake and a
common positive reference edge speed. The junction and momentum march
are standalone validation tools.

## Junction and wake reduction

For local velocity ratio `q = u / Ue`, the three integral lengths are
the transverse integrals of `1 - q`, `q(1 - q)` and `q(1 - q²)`.
The junction adds the two surface contributions after projection onto
a common plane with equal edge states. A stationary trailing-edge gap
adds only displacement. The thin-layer junction imposes no base-pressure
force and requires separate matching if the two edge states differ.
[Fidkowski, equations 5 and 14](https://doi.org/10.2514/1.J061341)
[Drela, blunt trailing-edge analysis](https://doi.org/10.2514/6.1989-2166)

Given a uniform-static-pressure plane of finite width, these same
moments determine the mass-averaged survey total pressure and the
mixed-out total pressure. The latter follows from conservation of
mass and normal momentum. On the DCA 152.6% chord traverse, the two
edge-to-wake losses, in inlet dynamic heads, are 0.018554 and 0.019942.
The independent perfect-gas reduction of the same measured profile
gives 0.018601 and 0.020003. Both reductions use the projected-pitch
width and edge speed from the earlier wake audit. The difference
between survey and mixed-out loss survives the low-speed limit.
[Earlier wake reduction](phase3_wake_flux_v16.md)

The free-wake momentum equation at zero wall shear is
`d ln(theta) = -(2 + H) d ln(Ue)`. The march uses measured `H = delta*/theta`
and `Ue` at every station and one measured initial `theta`. Piecewise
shape-preserving interpolation of `H` and `ln(Ue)` closes the integral
between stations. This tests the compatibility of the momentum equation
with the survey history. Prediction of wake shape needs a separate equation.

## NASA DCA at −8.5° incidence

The surface Reynolds numbers at 98.4% chord on the pressure side and
97.6% chord on the suction side are 647 and 2270. When expressed at one
nominal edge speed, their combined momentum thickness is 1.690 mm
(`Re_theta = 2917`). Adding a stationary gap equal to the geometric
edge diameter of 1.829 mm changes displacement from 3.250 to 5.079 mm
with the same momentum thickness. The first wake survey gives
2.617 mm (`Re_theta = 4517`). The approximate common-edge budget
leaves a gap between spatially distinct surveys. The calculation cannot
identify a base-pressure force or isolate its share of the difference.
[NASA CR-185118 Volume I, Table 15](https://ntrs.nasa.gov/citations/19900000722)

Use the arithmetic mean of the first and last printed velocity
samples in each transverse profile as an edge-speed proxy.
[NASA CR-185118 Volume II, Tables 77–80, printed pp. 113–120](https://ntrs.nasa.gov/citations/19900000723)

| Chord station | Edge proxy (m/s) | Reported H | Reported Reθ | Marched Reθ |
|---|---:|---:|---:|---:|
| 106.0% | 25.895 | 1.65 | 4517 | 4517 |
| 109.7% | 25.525 | 1.54 | 4330 | 4689 |
| 131.9% | 24.790 | 1.25 | 3510 | 5027 |
| 152.6% | 24.005 | 1.19 | 3107 | 5398 |

The reported Reynolds number falls 31.2%. The conditional march rises
19.5%. Using either outer sample separately yields 5220 to 5578 at the
last station and preserves the sign mismatch. With the measured shape
history and a log-linear speed history, the reported Reynolds-number
drop would require an edge-speed increase of 17.5%. The edge proxies
decrease by 7.3%. Changing the positive shape history alone cannot
reverse the sign for a monotonically decreasing edge speed.

Possible contributors include the two sides of the wake having different
outer states, streamwise stress transport, confinement and different
survey methods. This comparison cannot attribute the difference among
these effects. A full momentum balance needs pressure and velocity on
a common control surface with a consistent projected coordinate and
measurement convention.

[Archived DCA comparison](../validation/campaigns/20261105T184404389654Z_slc_aungier_experimental_v16/analysis.json)

## Independent planar-wake measurements

The Liu, Thomas and Nelson symmetric planar wakes cover nominal zero,
adverse, moderate favorable and strong favorable pressure gradients.
Each wake uses its earliest available measured station as the initial
condition. Average repeated transverse coordinates before trapezoidal
integration. Use the mean of the outer five samples on each side for
`Ue`, and repeat with three and eight to expose reduction sensitivity.
Integrate across the recorded survey width and retain signed pointwise
defects. The outer samples provide edge proxies and the three reductions
are sensitivity checks, without a statistical uncertainty estimate.
[Experiment](https://doi.org/10.1063/1.1490349)
[Turbulence Modeling Resource profiles](https://tmbwg.github.io/turbmodels/Other_exp_Data/wake_planar_exp.html)

| Pressure gradient | Stations | Measured initial θ (mm) | Measured final θ (mm) | Marched final θ (mm) | Final relative error | Largest station error |
|---|---:|---:|---:|---:|---:|---:|
| Nominal zero | 9 | 6.993 | 6.643 | 7.214 | +8.6% | 19.4% |
| Adverse | 10 | 6.333 | 13.619 | 12.401 | −8.9% | 8.9% |
| Moderate favorable | 11 | 6.341 | 2.606 | 3.033 | +16.4% | 16.4% |
| Strong favorable | 11 | 7.750 | 0.940 | 1.585 | +68.6% | 68.6% |

The march reproduces the direction of the change in the three forced
pressure gradients. The nominal zero-gradient march gives a small
increase and the measured thickness decreases slightly. Under strong
acceleration the final error remains +52.8% to +107.9% across the
three tail reductions. This establishes a trend check for a limited
low-speed application. It leaves quantitatively predictive loss, strong
acceleration and the DCA sign mismatch outside the supported scope.

The original archive accompanies the campaign. Reproduce the reductions
with `python -m validation.probe_planar_wake_momentum PATH_TO_ARCHIVE`
and the DCA comparison with `python -m validation.probe_wake_junction`.
Both repeat their calculations and verify the frozen v16 source and
runtime. All 40 targeted tests pass, including the junction, finite-width
mixing and the exact constant-shape momentum law.

[Archived planar-wake comparison](../validation/campaigns/20261105T184954023959Z_slc_aungier_experimental_v16/analysis.json)
[Original profile archive](../validation/campaigns/20261105T184954023959Z_slc_aungier_experimental_v16/symmetricwake-uvcorrected.zip)

The next cascade comparison needs matched surface and wake momentum
budgets with pressure evidence before introducing a momentum source.
Stage 35–38 efficiency ordering and qualification for training labels
remain open.
