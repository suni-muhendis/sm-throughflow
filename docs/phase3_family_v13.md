# Stage 35–38 loss attribution and actual-incidence shock correction

Simulator: `slc_aungier_experimental_v13`. The score remains disabled and the
family-efficiency acceptance gate remains **failed**. This iteration fixes an
internal shock-model inconsistency; it does **not** fix the measured family
ranking or qualify the model for teaching a design model which compressor is
more efficient. Keeping this distinction is necessary even though the source
equation is implemented more faithfully.

## Matched results against v12

All 108 frozen jobs were rerun with the same experimental readings, designs,
operating points and numerical budgets; only the required simulator version
changed. Both original and projected geometry interpretations are retained.

| Outcome | v12 | v13 |
|---|---:|---:|
| Converged, all requests | 75/108 | 74/108 |
| Original geometry | 35/54 | 34/54 |
| Projected geometry | 40/54 | 40/54 |
| Stage 35–38 coupled readings, each representation | 17/17 | 17/17 |
| Original Stage 53 coupled readings | 3/5 | 2/5 |

There are no gained successes. The single loss is original Stage 53 reading
2993: the last quasi-normal iteration exhausts 200 passes with residual
0.11150 after the retained startup/fallback attempts. Its classification is
`numerical_failure`, with `physical_limit_established=false`; no new physical
choke boundary is inferred. The projected counterpart remains converged.
All original Stage 35 readings, including the previously recovered 90% point,
remain converged. Repeated anchor outputs match bitwise in both interpretations.
No supersonic compression clipping occurs in returned coupled solutions.

The original-annulus peak-flow anchors give:

| Stage | Measured eta (%) | v12 eta (%) | v13 eta (%) |
|---|---:|---:|---:|
| 35 | 84.5000 | 82.2048 | 81.2099 |
| 36 | 82.1000 | 82.3459 | 81.7005 |
| 37 | 84.0000 | 82.5116 | 81.7185 |
| 38 | 83.1000 | 82.9849 | 82.2999 |

| Family difference, eta points | Measured | v12 | v13 |
|---|---:|---:|---:|
| 35→36, aspect ratio at low loading | -2.4000 | +0.1411 | +0.4906 |
| 37→38, aspect ratio at high loading | -0.9000 | +0.4734 | +0.5813 |
| 35→37, loading at low aspect ratio | -0.5000 | +0.3067 | +0.5087 |
| 36→38, loading at high aspect ratio | +1.0000 | +0.6390 | +0.5993 |

Both aspect-ratio directions remain reversed and worsen. The three frozen
legacy comparisons starting from Stage 35 also remain reversed. The fourth,
36→38, already has the measured direction; it is not a newly passed gate.

On common successful **experimental coupled** readings, broader P90 absolute
errors move as follows. The original cohort excludes the lost Stage 53 point
from **both** versions; that loss is separately counted above. These cohorts
differ from the smaller v11/v12 common cohorts in the previous report.

| Interpretation / paired readings | PR-rise relative error v12→v13 | Eta error v12→v13 (points) | Rotor TR-rise error v12→v13 |
|---|---:|---:|---:|
| Original / 22 | 23.1677%→23.1386% | 4.4197→4.0167 | 15.7990%→14.9231% |
| Projected / 28 | 21.7486%→21.5710% | 4.5263→3.8945 | 15.3871%→15.0254% |

Thus some aggregate errors improve while this family's ordering worsens and
one numerical solution is lost. Aggregate improvement is not a qualification
of the family response.

The 96 measured-state row closures and six adapter-sensitivity results were
also recomputed. Conditioning on measured inlet and exit meridional state
isolates the loss closure from coupled-flow convergence. Core equal-sample
rotor loss means at the anchors are:

| Rotor | Reported total loss | v12 closure | v13 closure |
|---|---:|---:|---:|
| 35 | 0.10820 | 0.16595 | 0.15981 |
| 36 | 0.13180 | 0.15932 | 0.15591 |
| 37 | 0.11860 | 0.18727 | 0.18388 |
| 38 | 0.14480 | 0.18596 | 0.18262 |

The higher-aspect-ratio rotor has **higher measured** core loss in both pairs,
but **lower predicted** loss even with measured meridional conditions supplied.
This localizes a remaining error to the closure/represented blade model; it
cannot be repaired solely by tightening the outer throughflow convergence.
These are diagnostic radial-sample means, not independent rig replicates or
additive efficiency budgets. Rotor exit states are reconstructed by the NASA
data reduction, and reported shock/profile partitions are themselves model
based; neither is treated as an independent shock measurement.

## What was isolated

Four original-annulus anchors are the measured 100% speed peak-efficiency
readings: Stage 35/3978, 36/4272, 37/4182 and 38/4120. Thirty-two v12
counterfactual solves separately removed shock, leakage, Reynolds, profile
endwall, supercritical and off-design profile contributions, or substituted
the reports' PHISS. Eight additional solves tested actual-flow shock turning
with and without meridional projection; four tested nominal conical sections.
These 44 deliberately altered solves are diagnostic experiments, not new
experimental observations or release evidence. No fitted coefficient was used.

| v12 diagnostic override | Stage 35 eta (%) | Stage 36 | Stage 37 | Stage 38 |
|---|---:|---:|---:|---:|
| None | 82.2048 | 82.3459 | 82.5116 | 82.9849 |
| Shock removed | 90.7603 | 90.7373 | 90.0506 | Numerical failure |
| Clearance removed | 82.4066 | 82.4251 | 82.7243 | 83.1662 |
| Reynolds correction removed | 81.8206 | 82.0494 | 82.2507 | 82.7698 |
| Profile endwall term removed | 83.3928 | 83.1243 | 83.4001 | 83.5926 |
| Supercritical term removed | 82.3524 | 82.5490 | 82.8505 | 83.2923 |
| Off-design profile multiplier removed | 82.7675 | 83.0308 | 83.2797 | 83.8369 |
| Report-assumed PHISS substituted | 83.0129 | 82.5831 | 83.3358 | 83.2417 |
| Nominal conical sections | 82.4507 | 82.5932 | 82.7440 | 83.2165 |

These changes are nonlinear coupled re-solves, so their efficiency differences
are not additive loss budgets. Nevertheless, they locate strong sensitivity
in the rotor shock closure and the profile/endwall balance. Removing leakage,
Reynolds or the supercritical term does not repair the ordering. Eliminating
shock is physically inadmissible for these supersonic rotor inlets and loses
a Stage 38 solution. Eliminating endwall loss is likewise not a correction.
Nominal conical projection moves all four efficiencies similarly and does
not resolve the family response.

The existing profile endwall term scales with pitch/height; at otherwise
similar solidity it favors smaller pitch/high aspect ratio. The Reynolds
correction partly opposes that effect. A spanwise mean loss coefficient also
cannot alone determine efficiency: the four machines have different work,
diffusion, leakage, operating flow and radial distributions. The remaining
error is therefore a closure/model-form problem, not an identified single
coefficient with a justified replacement value. Shock/endwall interaction and
shock-foot geometry are priority hypotheses, not experimentally isolated
proof of the missing loss magnitude.

## Source-backed change

[NACA RM E57A30 Appendix B, printed pp. 23–25](https://ntrs.nasa.gov/api/citations/19930089514/downloads/19930089514.pdf?attachment=true)
uses the actual inlet relative direction minus the suction-surface tangent
at the assumed passage-shock foot for the Prandtl-Meyer turn. The old
assembly substituted surface turning from LE to foot. These expressions
agree only at tangent incidence:

```text
v12: delta_nu = suction_LE_angle - suction_foot_angle
v13: delta_nu = relative_inlet_flow_angle - suction_foot_angle
```

For constructed DCA/MCA profiles the simulator now carries both surface
tangents, projects them onto the row cone, and uses actual relative flow.
The cascade sign convention is tested for both rotor and stationary row.
Diagnostics expose `shock_flow_turning`, `suction_surface_incidence` and
`shock_compression_clipped`. The last indicates a supersonic negative turn
for which the expansion-only closure retains its zero-expansion floor. It is
not interpreted as a physical choke or stall limit.

The foot-location approximation, arithmetic mean shock Mach, geometric
sampling, coefficients, profile/deviation/leakage models, residual tolerances,
wall count and iteration budgets are retained. NACA65/C4 still use the
analytic tangent-entry approximation; they are not covered by this fix.
The foot remains precomputed on cylindrical design sections and sampled at
inlet span, so in-row streamline migration and exact conical surface layout
remain limitations. There is still no coupled bow-shock/boundary-layer model.

## PHISS interpretation and rejected shortcut

The individual reports define PHISS as surface camber ahead of an **assumed**
shock location: [TP-1338 Appendix C, printed p. 18](https://ntrs.nasa.gov/api/citations/19790001889/downloads/19790001889.pdf),
[TP-1974 Appendix C](https://ntrs.nasa.gov/api/citations/19820011348/downloads/19820011348.pdf),
and [TP-2001 Appendix C, printed p. 9](https://ntrs.nasa.gov/api/citations/19820014395/downloads/19820014395.pdf).
This is not an independent measured shock position. It must also be
distinguished from front-segment camber to the transition in TP-1337 eq. B3.
An intermediate investigation incorrectly equated these definitions; that
interpretation is withdrawn. The archived PHISS counterfactual remains useful
only as sensitivity to the source's assumed geometry/foot location.

Substituting the four reports' PHISS improves both aspect-ratio orderings, but
does not establish a general geometry-to-shock-location algorithm for newly
generated blades. Hard-coding those table values into the simulator would
hide a model assumption behind case identity. It was not adopted.

## What the family comparisons mean

At 100% speed, Stage 35→36 and 37→38 compare aspect ratio at the two design
loading levels. Stage 35→37 and 36→38 compare loading at the two aspect
ratios. All use different measured peak-flow anchors and have other geometry
and clearance differences; none is a controlled partial derivative.
The frozen legacy three comparisons from Stage 35 are still reported.

[NASA TP-1337, discussion of loading and aspect ratio](https://ntrs.nasa.gov/api/citations/19780025165/downloads/19780025165.pdf)
supports a low-aspect-ratio efficiency advantage in this family, but not a
universal rule that increasing loading must reduce efficiency at every speed
and flow. In particular, the small 35→37 peak-efficiency difference cannot be
turned into a universal training constraint. No acceptance threshold or
experimental target has been changed to make v13 pass.

## Implication for design training

Conservation, repeatability and sensible local incidence response are necessary
but insufficient. These cases still cannot provide trusted labels for the
efficiency benefit of aspect ratio or loading. Preserve numerical failures,
model warnings and version identity in any development dataset, and keep
performance-based design ranking disabled.

The next physics work needs an independently checked surface/foot model and
a transonic loss closure that captures the relevant three-dimensional
interactions, with coefficients established independently of these four
anchors and checked on held-out machines. Replacing this with an empirical
Stage 35–38 efficiency offset would not meet the intended tool standard.

## Frozen evidence and verification

| Evidence | Campaign |
|---|---|
| v12 baseline | [20261104T225400132975Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225400132975Z_slc_aungier_experimental_v12/manifest.json) |
| 108 matched jobs + 96 row closures + 6 sensitivities | [20261104T232522087684Z_slc_aungier_experimental_v13](../validation/campaigns/20261104T232522087684Z_slc_aungier_experimental_v13/manifest.json) |
| Final analysis | [20261104T233526128041Z_slc_aungier_experimental_v13](../validation/campaigns/20261104T233526128041Z_slc_aungier_experimental_v13/manifest.json) |
| Final audit | [20261104T234011745189Z_slc_aungier_experimental_v13](../validation/campaigns/20261104T234011745189Z_slc_aungier_experimental_v13/manifest.json) |
| Diagnostic probe 1 | [20261104T230545829386Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T230545829386Z_slc_aungier_experimental_v12/manifest.json) |
| Diagnostic probe 2 | [20261104T230916451235Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T230916451235Z_slc_aungier_experimental_v12/manifest.json) |
| Diagnostic probe 3 | [20261104T231844330158Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T231844330158Z_slc_aungier_experimental_v12/manifest.json) |

![Matched family efficiencies](../validation/campaigns/20261104T233526128041Z_slc_aungier_experimental_v13/family_efficiency.png)

The complete suite passes **256 tests with one import-order skip**. The
skipped lazy-import test passes in isolation: **257 distinct tests verified**.
This includes the previously recovered Stage 35 90% point and both original
and projected eightfold-grid regressions at unchanged tolerances. Six new
tests cover fixed-Mach incidence response in both frames, tangent-entry
equivalence, conical projection, the compression flag, subsonic zero shock,
independent analytic circle geometry and malformed input. Historical
v5-v12 goldens, all 811 protected historical files, 114 v12 baseline JSON
artifacts and the frozen protocol checksum are unchanged.

The numerical campaign records production SHA256 `559a7af4f07937af32f242bc2cce3bec489204d4a7e3f44ab87a20f4bbb1035a`.
Final source SHA256 is `4863be0b501b6c84e11a5f096a9937617447daf8031044b001ccfa2d9f62ccc5`. The only intervening package
change corrects the PHISS definition in a docstring. An exact allowlisted
text diff and a docstring-stripped AST comparison verify identical executable
source; every other package file is byte-identical. Results retain their
original source identity and were not relabeled. The complete final test
suite runs against the final source. See `source_comparison.json` in the audit.

The initial v13 campaign `20261104T232255932514Z_slc_aungier_experimental_v13`
had a stale schema literal and is superseded, not physical evidence. The
initial full tests also exposed an inaccessible default temporary directory;
the final complete run uses a repository-local pytest directory. All initial
and final logs remain distinguished in the audit. The intermediate analysis
`20261104T233331876943Z_slc_aungier_experimental_v13` is superseded by the
final analysis above. No commit or publication is part of this iteration.
