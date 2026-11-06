# Stagnation initialization and passage displacement feedback

This work adds two research components for an eventual blade-passage
interaction model. The first computes a laminar initial state near
stagnation. The second solves a prescribed-flow symmetric channel with
displacement feedback and classifies its capacity constraints.

## Stagnation limit

For a known stagnation point, use the local edge expansion `Ue = K s`.
At this limit the edge is at the total thermodynamic state and `H = Hk`.
Let `F = Cf Re_theta` and `D = (2 Cd/H*) Re_theta`. Balancing the terms
proportional to `1/s` in the direct-march momentum and shape equations gives

    2 (2 + Hk) D = 3 F
    theta² = F nu / [2 K (2 + Hk)]

The same laminar closures are used as in the direct march. The first
three edge knots determine the quadratic estimate of the stagnation
slope. The first positive knot is initialized with the limiting state.
The caller supplies the position of stagnation and resolves its nearby
velocity gradient. [Fidkowski, section IV.C](https://doi.org/10.2514/1.J061341)

An independent numerical Hiemenz solution gives
`theta / sqrt(nu/K) = 0.292344` and `H = 2.216229`. The integral
initialization yields 0.291235 and 2.229508, errors of −0.38% and
+0.60%, respectively. The low-speed march retains the corresponding
constant thickness on a linear stagnation edge. The previously archived
NASA DCA march from an observed initial state repeats exactly. Its
first suction-side pressure tap is already at positive speed, so the
new stagnation initializer is verified independently of that case.
[NASA TP-3623](https://cs.odu.edu/~mln/ltrs-pdfs/NASA-97-tp3623.pdf)

## Displacement feedback in a symmetric channel

At each wall-arc knot the geometrical gap is normal to the common flow.
The two identical wall layers reduce it by twice the displacement
thickness. The subsonic area–Mach inversion gives a core speed and
pressure at prescribed mass flow per unit span and fixed core total
state. That speed drives the laminar layer march. The interaction
iteration damps the displaced gap update and requires both the gap and
mass residuals to pass the same explicit tolerance. It reports those
residuals on the supplied knots. [NASA Glenn compressible mass flow](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/mass-flow-rate-equations/)

At the inlet, momentum thickness and kinematic shape are supplied.
The compressible shape closure gives a displacement-corrected gap of
the form `a - b M²`. The maximum mass flux is found by differentiating
`(a - b M²) M / (1 + 0.2 M²)^3` on the subsonic branch. A Mach
sweep independently checks the maximum. This admission bound uses the
given inlet layer and does not depend on a downstream iteration.

The reference has a common, isentropic core. Its static pressure change
reflects area and speed changes. Viscous dissipation is reported by the
layer and has yet to be coupled to core stagnation pressure. Blade
surface loading, shock motion, transition and reattachment need their
own equations before applying this model to an asymmetric cascade.

## Manufactured channel results

The gap is 12 mm, the length is 60 mm, and the two incoming layers each
have momentum thickness 0.09 mm and kinematic shape factor 2.59.
The core total state is 100 kPa and 300 K. Flow fractions below use
the ideal sonic capacity of the bare gap as denominator.

| Flow fraction | Outcome | Exit Mach | Exit pressure, bare → displaced (kPa) |
|---|---|---:|---:|
| 0.40 | Converged | 0.25245 | 96.085 → 95.664 |
| 0.75 | Converged | 0.53839 | 84.109 → 82.099 |
| 0.90 | Converged | 0.75540 | 73.491 → 68.506 |
| 0.95 | Unresolved trial displacement capacity | — | — |
| 0.98 | Infeasible prescribed inlet layer | — | — |
| 1.02 | Infeasible bare geometry | — | — |

The supplied inlet layer bounds admission at 95.2505% of bare sonic
capacity. At 95%, the inlet bound permits the request and a downstream
trial runs out of effective area. That result leaves the true limit of
the coupled reference unresolved. Exhausting an iteration budget has a
separate classification.

At 40%, increasing the knot count from 17 to 65 changes the exit pressure
by about 0.000033 Pa. Every converged case satisfies a relative mass
residual below 1e-8. The eight sweep records repeat exactly. The 30
targeted tests include the Hiemenz comparison, the independent inlet
capacity sweep, mass conservation and failure classifications.

[Reproducible campaign](../validation/campaigns/20261105T155713359611Z_slc_aungier_experimental_v16/analysis.json)

The next experimental gate remains a passage calculation with separate
pressure- and suction-side edge histories, matched to the measured
surface pressure and shock position at the TEAMAero conditions. Only
then can the post-shock layer and wake be compared on consistent planes.
The v16 package source identity was verified against its frozen
baseline. Stage 35–38 efficiency ordering remains open.
