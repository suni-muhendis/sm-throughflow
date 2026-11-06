# Direct laminar blade-layer calculation

The research solver advances momentum and kinetic-energy thickness on a
prescribed smooth edge segment. It provides displacement and dissipation
from the same state for future coupling to blade-passage flow. The current
comparison finds late growth and late separation on a low-speed DCA blade.

## Equations and scope

[`blade_layer_reference.py`](../validation/blade_layer_reference.py) uses
Fidkowski's momentum and kinetic shape equations (5)–(6) with zero wake gap,
the laminar shape closures (45)–(48), skin friction (56) and dissipation
(61). The implementation integrates squared momentum thickness and the
kinematic shape factor, differentiating (47) analytically. Static
temperature, density and Mach number follow from the supplied edge speed
and constant total state. Air viscosity uses the same Sutherland law as
the throughflow endwall model. The paper's closure equations are used on
smooth branches. Its subsonic potential-flow solver is outside this
implementation. [Fidkowski, AIAA Journal](https://doi.org/10.2514/1.J061341)

The solver accumulates viscous dissipation power per unit span by
integrating `c_D rho_e U_e^3` along the wall. This is a local layer
quantity. It does not include shock entropy or downstream mixing. The
attached march terminates when the modeled wall shear crosses zero.
Prescribe initial momentum thickness and kinematic shape factor at a
positive edge velocity. Split the inputs at a shock. The march has no
transition, reverse-flow, reattachment or shock-jump law. A failed ODE
solve raises an error separately from the zero-shear event.

## Conditioned experimental comparison

The NASA DCA suction-side case at −8.5 degrees incidence has an attached
laminar region followed by a long separation bubble. Table 13 supplies the
pressure-tap edge-speed history. Table 15 provides the initial state from
the authors' Falkner–Skan fit at 10.4% chord and comparison states farther
downstream. The suction circle from Appendix A converts chord coordinates
to wall arc length. The nominal 300 K total temperature is an assumption.
The reference total pressure is set by the report's kinematic viscosity
at the initial station. No aerodynamic coefficient is fitted to this case.
[NASA CR-185118](https://ntrs.nasa.gov/citations/19900000722)

| Station | Calculated Reθ | Reported spline-fit Reθ | Reported Falkner–Skan Reθ |
|---|---:|---:|---:|
| 19.7% chord | 206.9 | — | 247 |
| 30.1% chord | 285.1 | 266 | 334 |

At 30.1% chord the calculated displacement thickness is 0.333 mm and
the kinematic shape factor is 2.951. The corresponding low-speed shape
factors in the report are 3.22 (spline) and 3.08 (Falkner–Skan). The
nominal march first crosses the report's separation proxy, H₁₂ = 3.5,
at 37.108% chord versus the authors' estimate of 31.9%. Its own wall-shear
zero is at 38.402%. The report's separation estimate comes from a
profile fit and does not supply a measured wall-shear zero.

Starting from the authors' later state at 19.7% moves the model proxy
to 33.546% and zero shear to 34.388%. At 30.1%, this run gives Reθ 320.7
and displacement thickness 0.392 mm. This is an initial-state sensitivity
check and consumes the 19.7% observation as input. The nominal zero-shear
location changes by approximately 0.000002 percentage points when the
integration tolerance is tightened by 100×. A nominal repeat is exactly
equal. The discrepancies are larger than the observed integration error.

[Source data](../validation/cases/nasa_dca_cascade_layer/notes.md) and
[campaign output](../validation/campaigns/20261105T154938498230Z_slc_aungier_experimental_v16/analysis.json)

The 23 targeted tests include the Blasius limit, a kinetic energy balance,
termination under adverse pressure gradient, a manufactured smooth
transonic edge and earlier shock and wake checks. The full coupled
compressor experiment was outside this component run. Package source and
runtime identity were verified against the frozen v16 campaign.

The next comparison needs a trustworthy upstream layer state and a
coupled pressure response. Start from stagnation or an independently
measured upstream state, and check the layer before and after the
interaction on the same experimental run. The TEAMAero targets and
conservative wake reduction are described in the
[shock and wake study](phase3_wake_flux_v16.md). Stage 35–38 ranking
remains open.
