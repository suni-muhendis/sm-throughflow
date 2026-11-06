# Rotor 35–38 casing pressure and passage-shock screening

## Experimental comparison

Figure 8 of NASA TM-79280 gives time-averaged casing static pressure
divided by rotor inlet total pressure at design speed. The horizontal
coordinate is axial distance from the tip leading edge divided by the
tip projected chord. Figure 9 shows the lowest-flow conditions on a
dimensional axis and provides a visual cross-check of the different
pressure-rise shapes.
[NASA TM-79280, Figures 8 and 9](https://ntrs.nasa.gov/citations/19800002791)

The reduction records 101 marker centres from the 12 curves in
Figure 8. The PDF page, render resolution, crop, separate axis
calibrations, plotted flow strings, marker symbols and pixel positions
are retained. The leading-edge points where markers crowd or overlap
were excluded. The reduction uses the plotted points and excludes the
smoothed lines drawn between them. Each plotted flow matches a unique
reading at design speed in the existing rotor tables. For example,
the middle Rotor 38 curve at 20.83 kg/s is reading 4121, while the
efficiency attribution uses 20.67 kg/s and reading 4120.
[Pixel picks and reading matches](../validation/studies/tm79280_figure8_pixels.json)

Piecewise-linear interpolation gives pressure differences over fixed
chord windows. A four-pixel allowance in each direction covers approximate
marker picks and axis placement. Each pressure envelope includes every
point on the interpolated curve over its axial tolerance interval and
adds the vertical tolerance. Pressure differences use conservative
endpoint envelopes. These bands describe digitization sensitivity.
The experimental uncertainty of the casing pressure is separate.

At the lowest plotted flow of each rotor, the centre estimates are
as follows. The final column shows the difference between two
equal-length windows and its digitization band.

| Rotor | Flow (kg/s) | Rise over 45–60% chord | Rise over 60–75% chord | Difference and band |
|---|---:|---:|---:|---:|
| 35 | 18.20 | 0.082 | 0.056 | 0.026 [−0.063, 0.114] |
| 36 | 20.26 | 0.196 | 0.028 | 0.168 [0.081, 0.249] |
| 37 | 19.60 | 0.152 | 0.082 | 0.070 [−0.032, 0.167] |
| 38 | 20.44 | 0.191 | 0.022 | 0.169 [0.081, 0.249] |

For Rotors 36 and 38 the mid-chord rise exceeds the following rise
throughout the digitization band. At the highest plotted flow their
centre differences are −0.033 and −0.073, with both bands spanning
zero. The strongest local compression and the subsequent recovery
must therefore be compared across operating points. The low-flow
centre differences for Rotors 35 and 37 are smaller, with overlapping
bands between rotor families. These wall-pressure measurements give
no direct blade-surface shock coordinates or separated-flow lengths.

## Matched candidate screening

The existing inviscid passage-shock candidate was run on the same
12 inlet and reconstructed exit states. The outermost survey is 5%
from the tip. The wall state is extrapolated from the radial surveys
and kept separate from the measured sample. The rotor exit static
pressure supplied to the candidate comes from the row reconstruction.
The casing curve remains a separate comparison.

- The candidate evaluates all 12 outermost sections on its unchoked
  branch. This is its internal regime decision. The candidate ignores
  the supplied exit back pressure on that branch and supplies a
  section suction-surface shock foot and a total-pressure loss.
- The candidate supplies zero axial casing-pressure profiles. Its
  suction-surface foot coordinates cannot stand in for measured casing
  pressure or for the chordwise position of its maximum gradient.
- The shock component alone exceeds the reported total rotor loss in
  seven of the twelve outermost measurements and exceeds both the
  reported and reconstructed totals in six. For Rotor 36 at 20.94 kg/s,
  the candidate gives 0.20550 against 0.17000 reported and 0.16916
  reconstructed. These totals and estimates use the inlet relative
  dynamic-head basis and retain the uncertainty of the reported
  reconstruction.
- At the extrapolated tip, a thermodynamic ceiling uses the candidate's
  shock total-pressure ratio with the relative stagnation enthalpy
  implied by rothalpy conservation and the exit radius. Even the
  tighter conditional check using the reconstructed exit velocity
  stays at or above the lower edge of the casing trailing-edge
  digitization band in all cases, with either local or mass-averaged
  inlet pressure as the reference.
  This one-sided check cannot establish pressure recovery or validate
  the candidate.

The candidate fails the near-tip loss screen and cannot be compared on
the measured pressure distribution. A subsequent candidate needs a
chordwise mean pressure prediction with a common mass flow and pressure
compatibility, and a viscous recovery law that predicts both entropy
and blockage. Compare the complete distributions and the fixed
pressure-rise windows before the full 108-job comparison. The separate
35 → 37 stator loss check remains part of the same acceptance work.
[Rotor and stator loss attribution](phase3_stage_loss_attribution_v16.md)

The final reduction repeats exactly and verifies the frozen v16
source and runtime. All 33 targeted tests pass. The first archive
attempt stopped during JSON serialization of a NumPy boolean. The
final archive uses native scalar values and preserves the initial
manifest separately. This experiment leaves the ranking and
training-label qualification open.

Reproduce with `python -m validation.audit_rotor_casing_pressure`.
[Archived pressure curves and candidate results](../validation/campaigns/20261105T192433616591Z_slc_aungier_experimental_v16/analysis.json)
