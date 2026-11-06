# Fixed-mass passage with a prescribed exit pressure

## Conservation reference

The quasi-one-dimensional reference takes fixed mass flow, geometric
area, mass-displacement area and relative stagnation temperature along
the passage. In a rotor, the relative stagnation enthalpy follows
`I + (Omega r)^2 / 2` with fixed rothalpy `I`. The inlet entropy fixes
the upstream relative stagnation pressure at each radius. The normal
shock is a discontinuity separating two isentropic core branches.
[NACA Report 1135, continuous flow and normal shocks](https://ntrs.nasa.gov/citations/19930091059)

At the unmixed outlet, the prescribed static pressure and mass flow
give the unique positive exit Mach from
`M_e sqrt(1 + (gamma-1) M_e^2 / 2)`. With a subsonic exit this fixes the
downstream stagnation-pressure ratio. Inverting the normal-shock
relation gives the required upstream shock Mach. Its area ratio then
gives the possible shock positions. The effective area divided by the
upstream critical area is interpolated piecewise linearly. Every
intersection is checked for downstream capacity before accepting a
unique internal shock. A flat interval at the required ratio and
multiple compatible positions are reported as ambiguous.

The model reports insufficient area capacity, incompatible exit state
and unavailable internal shock separately. Those statements apply to
the prescribed stream sheet and closure. The classifications give no
independent physical choke or stall boundary for the complete rotor.

## NASA geometry and attached wake hypothesis

The twelve Figure 8 flows use their matched inlet and reconstructed
outlet states. Actual MCA surface and edge-circle intersections provide
the axial solid width. The open pitch projected normal to the mean
relative flow gives the area, with the radial strip width interpolated
from the reported inlet and outlet radii. The two turning histories use
the measured endpoint angles. The first uses linear turning, and the
second adds the chordwise curvature of the constructed camber line
with its endpoint trend removed. Neither uses the casing pressures as
input. The unknown true interior stream-sheet shape and turning
remain geometric assumptions.
[Matched Figure 8 conditions](phase3_rotor_casing_pressure_v16.md)

The attached case subtracts two turbulent flat-plate mass-displacement
thicknesses using inlet unit Reynolds number and the streamwise arc.
The one-seventh-power profile gives `H = 9/7` and the Prandtl
flat-plate drag law gives `theta = 0.037 x Re_x^-1/5`. The single
attached prescription supplies the displacement and the same exit
wake profile. The wake reduction integrates mass, momentum and
enthalpy to distinguish survey loss from mixed-out loss.
The prescribed growth has no pressure-gradient or shock-separation
response, and it represents blade layers without tip-clearance or
endwall interaction.
[NASA CR-2333, flat-plate drag law](https://ntrs.nasa.gov/citations/19740010566)
[Conservative wake reduction](phase3_wake_flux_v16.md)

## Pressure and loss results

| Scope | Matched internal shock | Insufficient ideal capacity | Required shock area outside passage |
|---|---:|---:|---:|
| All measured and extrapolated slices and four variants | 6 | 114 | 72 |
| Extrapolated casing only | 3 | 19 | 26 |

Only the Rotor 37 reading at 19.60 kg/s supplies compatible casing
solutions. All three place the normal shock between 96.3% and 97.8%
of projected chord. The attached linear-turning case matches the
imposed exit pressure to a relative error below 1e-15 and conserves
mass on the grid to about 3.1e-15. It predicts a pressure-ratio drop
of 0.079 from 60% to 75% chord, where the measured casing ratio
increases by 0.082. The casing pressure-ratio RMS errors are 0.621
to 0.824 across the three accepted boundary matches. All interior
casing taps lie ahead of the predicted shock, so a downstream
pointwise error is unavailable. The imposed exit pressure gives
no independent validation of the internal pressure history.

At the extrapolated casing, the attached variant gives a shock
loss of 0.3897 and a mixed-out loss of 0.3942, against reconstructed
total loss 0.2847. At the 50% measured span the attached case gives
0.1798 mixed-out, against 0.1490 reported and 0.1536 reconstructed.
The inviscid 70%-from-tip case gives 0.1198, close to the reported
0.1150 and reconstructed 0.1210. The matched subsonic exit state
does not establish a usable family response.

Increasing the chord grid from 161 to 321 stations preserves all
192 classifications. The largest shock-position change is 0.145
percentage points of projected chord. All casing shock shifts
are below 0.001 percentage points. The closure and stream-sheet
representation dominate the observed discrepancies at this resolution.

## Blockage comparison

NASA TM-107310, Figure 55 supplies a separate same-rotor blockage
check at design speed and 70% span from the hub. Use the last
suction-surface marker in each panel, at approximately 98% chord.
The plotted quantity is based on velocity displacement. In the
adiabatic one-seventh-power wake used here, the layer density is
at most the edge density, so the modeled velocity displacement
cannot exceed the mass displacement. This gives an upper bound
for the model's suction-side contribution under its common normal
projection.
[Figure 55 pixel readings](../validation/studies/tm107310_figure55_trailing_pixels.json)
[NASA TM-107310, equations 23–26 and Figure 55](https://ntrs.nasa.gov/citations/19970001675)

| Suder flow label | Measured suction blockage near 98% chord |
|---|---:|
| Low | 6.28% |
| High | 3.19% |
| Max | 3.39% |

The digitization allowance is approximately ±0.12 percentage points.
Across the three Stage 37 flows and both turning histories, the
attached hypothesis gives upper bounds of 0.64% to 0.73% at the same
span and chord. These values describe the prescribed layer even
where the internal shock branch fails. The two experiments use
different test configurations and flow labels. The gap is a
same-family screening result with no pointwise flow match or calibrated
error estimate. The downstream radial-area blockage in Table 6 is
retained separately because it has a different station and aggregation.

## Verification and remaining model work

The reference passes the analytic checks for outlet pressure, mass,
normal-shock momentum, back-pressure response, rejection of multiple
roots and wake conservation. All 43 targeted tests pass. The NASA
reduction repeats exactly against the frozen v16 source and runtime.

The single normal shock and attached displacement fail the joint
pressure, loss and blockage screen. A useful successor needs a
stream sheet that can redistribute radial mass flow and turn across
an oblique shock, plus a pressure-gradient and separation response
that changes displacement and entropy together. The present
results are research evidence. The whole-stage efficiency and
training-label gates remain open.

Reproduce with `python -m validation.probe_backpressure_passage`.
[Archived NASA comparisons and grid refinement](../validation/campaigns/20261105T202125703157Z_slc_aungier_experimental_v16/analysis.json)
