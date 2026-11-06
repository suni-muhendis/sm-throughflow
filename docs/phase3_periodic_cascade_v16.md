# Separate surface loading in a low-speed cascade

The periodic blade calculation predicts separate pressure- and suction-side
edge speeds and feeds both into the laminar march. This is a low-speed
research reference for testing geometry, loading and stagnation before
developing a compressible blade passage. The NASA DCA comparison exposes
both turning error and a leading-edge layer problem.

## Method

The velocity field uses constant source panels and one circulation
density, with the specified upstream velocity. The complex point-source
kernel for a row of identical blades is `(pi/p) coth(pi z/p)`, where
`p` is pitch and the periodic direction is imaginary. Subtract the
upstream limit. Integrate the singular isolated-panel part analytically
and the smooth periodic correction by Gauss quadrature. Exact zero net
source preserves the axial flux. A uniform collocation residual balances
that constraint and is reported separately. This is a periodic extension
of the constant-source and circulation construction.
[Hess and Smith](https://doi.org/10.1016/0376-0421(67)90003-6)

The NASA section uses the two published circle centres, 228.6 mm chord,
106.8 mm pitch, 20.5 degree stagger and 0.9144 mm edge radii. Reconstruct
the large circle radii for exact tangency to the small circles. The
resulting pressure and suction radii are 246.740 and 189.102 mm,
compared to the printed 246.8 and 189.1 mm. The default circulation
condition equates the outgoing speed at the last large-circle panel on
each surface. These are explicit choices for the rounded trailing edge.
[NASA CR-185118 Volume I, Table 1 and Appendix A](https://ntrs.nasa.gov/citations/19900000722)

The leading-edge sign change determines the stagnation location. March
each wall away from that point. Use a small first step proportional to
the distance from stagnation because the individual terms in the
equations have a 1/s scale. The previous measured-edge experiment,
which starts from an observed layer at positive edge speed, retains its
original integration settings.

## Results

On the finest mesh the pressure force agrees with the far-field
momentum and pressure balance to 0.2734%. This residual is 4.51% on the
coarsest mesh and approximately halves at each doubling. The maximum
normal residual on the finest grid is 2.49e-5 of inlet speed. The
pressure-coefficient RMS errors against Table 13 are 0.0645 and 0.1356
on the pressure and suction surfaces, respectively.

The predicted exit angle converges to −6.23 degrees. The measured angle
is −0.6 degrees. Equating surface speeds near 98% or 99% chord instead
of at the default panels changes the 192-panel-per-side angle to −2.92
or −4.60 degrees. The suction-side pressure error persists under both
changes. These positions are sensitivity probes and are not selected by
fitting the measured exit angle.

On fine meshes, the one-way direct marches from calculated stagnation
end near the leading edge on both surfaces. The authors observed possible
early separation and reattachment on the pressure surface. On the
suction side the finer meshes stop on the rounded nose. The 48-panel
case misses this early event and reaches much farther downstream. The
fine-mesh result cannot by itself predict the observed downstream bubble.
Volume I, printed p. 52 reports oil-film detachment at 35.3 ± 2.0%
chord, reattachment at 59.8 ± 2.3% and chemical-sublimation transition at
56.0 ± 0.8%. These observations are distinct from the 31.9% shape-factor
estimate discussed in the previous layer study.
[NASA CR-185118](https://ntrs.nasa.gov/citations/19900000722)

To isolate the downstream pressure effect, a separate suction-side
restart supplies the same measured initial layer at 10.4% chord as the
previous DCA study. With the calculated edge speeds, zero shear occurs
at 43.41% chord on the finest mesh. The measured-edge march gives
38.40% from the same initial state. The difference remains after
bypassing the early layer, so improving the initial state alone will
leave a downstream loading error.

The 32 targeted tests pass, including the isolated-cylinder pressure
limit, periodic control-volume force refinement and the preceding layer,
wake and shock checks. Five DCA meshes and two trailing-edge probes are
archived. The full 96-panel-per-side case repeats exactly. The campaign
verifies the package source and runtime against the frozen v16 baseline.
[Campaign results](../validation/campaigns/20261105T161139706235Z_slc_aungier_experimental_v16/analysis.json)

The remaining work includes coupling displacement to the two edge
histories and treating transition and reattachment. A transonic passage
also requires an outer-flow formulation that can represent shocks. The
observed turning and surface pressure discrepancies exclude this
reference as a throughflow row replacement.
