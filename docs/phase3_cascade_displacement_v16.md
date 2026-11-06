# Local blade displacement feedback and trailing-edge sensitivity

The periodic core and direct laminar layer now exchange pressure and
displacement on prescribed attached intervals. The DCA experiment below
isolates the suction-side contribution before the downstream bubble.
It resolves a local fixed point and does not improve the pressure or
turning agreement in this case.

## Coupling

The core uses the outward wall-normal speed obtained by differencing
the signed vertex values of `Ue delta*` along the closed contour.
The sign is positive with the contour on the pressure surface and
negative on the reverse-oriented suction surface. The flux difference
telescopes over the contour and the core enforces zero integrated
source strength. Kutta panels require zero prescribed normal speed.
An independent circular-cylinder harmonic checks the normal-to-tangent
response. An elliptical case with two attached patches checks symmetry
and mass balance with both surfaces active.
[Fidkowski, equation 23](https://doi.org/10.2514/1.J061341)

Within a patch the core supplies the tangential speed history and the
integral layer supplies displacement thickness. Multiply the resulting
defect by a squared sine window that vanishes at both ends. This
defines the applied perturbation and keeps the calculation local.
It introduces recovery at the patch boundary and is not a physical
wake closure. The layer solver still uses the unwindowed local edge
speed. The iteration closes the difference between applied and
recomputed normal velocity to 1e-7 of inlet speed. A trial separation,
edge reversal or integration failure has its own outcome. No missing
layer state is extrapolated through a separated region.

## Conditioned NASA DCA comparison

At −8.5 degrees incidence, use the suction-side state at 10.4% chord
from the earlier NASA comparison. Feed back only the attached interval
ending at 30.1% chord. Repeat with an end at 24.5%. The pressure side
responds through the common core, while its own displacement is held
inactive in this experiment. Repeat the earlier 98% and 99% chord
Kutta sensitivity probes, keeping their forcing outside the active
patch. Compare the coupled and impermeable-wall solution on the same
mesh and with the same Kutta panels.
[NASA CR-185118, Volume I Tables 13 and 15](https://ntrs.nasa.gov/citations/19900000722)

| Case | Baseline exit angle | Coupled exit angle | Suction Cp RMS at active taps, baseline → coupled |
|---|---:|---:|---:|
| Default, 192 panels per side | −6.218262° | −6.218343° | 0.04822 → 0.06749 |
| Default, 384 panels per side | −6.222174° | −6.222258° | 0.04844 → 0.06880 |
| Short patch, 192 panels per side | −6.218262° | −6.218299° | 0.04822 → 0.05708 |
| Kutta near 98%, 192 panels per side | −2.921626° | −2.921735° | 0.04824 → 0.06750 |
| Kutta near 99%, 192 panels per side | −4.604793° | −4.604888° | 0.04823 → 0.06750 |

The measured exit angle is −0.6 degrees. All six cases converge, with
19 or 20 interaction iterations and closed net prescribed flux.
The default 192-panel calculation has 0.291 mm displacement at the
end of the active layer. The peak imposed normal speed is 1.57% of
the inlet speed. Over all suction taps its Cp RMS changes from
0.13500 to 0.13666. Changes in the location of the Kutta condition
remain much larger than the local feedback effect on turning. This
comparison rejects this localized perturbation as a correction for
the DCA discrepancy. It leaves the effect of a complete blade layer
and wake interaction open.

[Archived paired results](../validation/campaigns/20261105T162948279995Z_slc_aungier_experimental_v16/analysis.json)

## Evidence for the remaining wake closure

In the incompressible reduction, the measured spline-fit values give
`Ue delta* = nu Re_theta H12`. With the report's `nu = 0.150 cm²/s`,
the last pressure and suction surface samples give 0.01504 and
0.06912 m²/s of displacement flow per span, respectively. The near
wake at 106% chord gives 0.11180 m²/s and the far wake at 152.6% gives
0.05546 m²/s. The wake decay across those planes is about 2.22% of
the inlet axial volume flux per pitch. The surface and wake values
refer to different survey planes. Their difference cannot be assigned
entirely to the trailing edge. A coupled wake needs a junction balance,
transition and reattachment through the measured bubble, and distinct
survey and mixed-out pressure definitions.
[NASA CR-185118, Volume I Table 15](https://ntrs.nasa.gov/citations/19900000722)

The 35 targeted tests pass. The nominal 192-panel comparison repeats
exactly, and the campaign verifies the v16 package source and runtime
identity. Stage 35–38 efficiency ordering remains open.
