# utrc_isolated_rotor: transcription notes

Source: NASA CR-3701 (Wagner, Dring, Joslyn 1983). PDF page = printed
page + 5. Low-speed isolated rotor (UTRC LSRR2), 28 blades, hub 24 in., tip
30 in., chord 6 in. constant, NACA 65-series thickness on a circular-arc
camber line, 510 rpm. Rotor alone (no stator) with thick inlet hub/tip
boundary layers (screens), so of limited use as a stage case.

## Files

- `CR3701_tableI_rotor_airfoil_geometry.csv`: θ1*, θ2* (metal angles from
  axial), t/B (max thickness / chord) and radius at 0, 25, 50, 75, 100 %
  span. Printed transposed; one line per span here.
- `CR3701_tableI_coords_span{0,25,50,75,100}.csv`: airfoil coordinates
  X, Y SUCT., Y PRES. (90 points per section; units not printed, inches by
  context: X runs from about -0.008 to 6.006 = chord 6 in.). The coordinate
  frame is not defined in the report; X appears to be along the chord line
  from the LE, Y normal to it (Y = Y_suct = Y_pres at the first and last
  points = LE/TE circle ends). The stagger printed above each section is in
  `scalars.json` (`stagger_per_section`).

## Reading procedure for the coordinate tables (important)

The coordinate pages are a degraded dot-matrix computer printout; the PDF
text layer is unusable. Every number was read from 300 dpi renders. In this
font a "6" and an "8" often both appear as a small closed lower loop, and
"0", "C", "D" and "3"/"5" can be confused. Therefore after reading, each
section was checked numerically:

1. X must increase monotonically with locally uniform spacing (it does in
   every section; spacing 0.0025 near LE/TE, 0.022, 0.151).
2. In every run of uniform X spacing, each Y value was compared with a
   quartic fitted through its six neighbours; residuals above 4e-5
   were re-examined at higher zoom.
3. The 100 % section is fore-aft symmetric to within a few 1e-5; mirror
   pairs were compared.

Where a re-zoom left the glyph ambiguous and the smooth fit (and, for 100 %,
the mirror value) clearly supported one reading, that reading is written
with a trailing '?'. The '?' cells are:

| section | X | column | written | note |
|---|---|---|---|---|
| 0 % | .19884 | Y PRES. | .04983? | 4th digit 6/8 glyph; fit gives .04984 |
| 0 % | 3.52821 | Y PRES. | .81888? | 6/8 glyph; fit .81888 |
| 0 % | 4.58655 | Y PRES. | .65383? | last two digits faint; fit .65381 |
| 0 % | 4.88894 | Y PRES. | .55883? | 6/8 glyph; fit .55888 |
| 0 % | 5.19132 | Y PRES. | .43924? | 4th digit faint (2?); fit .4391 |
| 25 % | .11510 | Y PRES. | -.01233? | 3/5 glyph; fit -.01232 |
| 25 % | 1.11229 | Y PRES. | .24197? | last digit illegible; fit .24187 |
| 50 % | 2.32063 | Y PRES. | .37984? | 6/8 glyph; fit .37984 |
| 75 % | .66059 | Y PRES. | .11286? | 6/8 glyph; smooth 2nd differences favour 8 |
| 75 % | 2.92455 | Y PRES. | .41086? | 6/8 glyph; fit .41087 |
| 75 % | 4.43385 | Y PRES. | .35085? | 6/8 glyph; fit .35085 |
| 100 % | .02349 | Y PRES. | -.00781? | 6/8 glyph; mirror -.00782 |
| 100 % | .18257 | Y PRES. | .04388? | 6/8 glyph; fit/mirror |
| 100 % | 1.86799 | Y PRES. | .40880? | 6/8 glyph; fit .40879 |
| 100 % | 4.13199 | Y PRES. | .40880? | mirror of the above |
| 100 % | 5.81741 | Y PRES. | .04387? | mirror of .04388 |
| 100 % | 5.88344 | Y SUCT. | .08437? | glyph looks like .06437, but the mirror value is .08437 and the fit gives .08438 |
| 100 % | 5.97648 | Y PRES. | -.00782? | 6/8 glyph |

The smoothness check only detects errors of about 4e-5 or more inside
uniform runs; an error in the 5th decimal, or in the few points at the LE/TE
spacing changes, would go unnoticed. Several 0-75 % cells read as "6" were
confirmed by the check; others with the same glyph that the check cannot
resolve are written as read.

## Other observations

- Table I radii (24.0 ... 30.0 in.) are equally spaced in span; 0 % span =
  hub (24 in.), 100 % = tip (30 in.). t/B varies linearly 0.09 to 0.06.
- θ1* is not monotonic in span (64.63 at hub, 58.20 at 25 %); θ2* = -14.77
  at the hub (negative = beyond axial). Kept as printed.
- Tip clearance: 2.3 % span at LE, 1.0 % at midchord, 3.3 % at TE; with a
  6 in. span these are the 0.14 / 0.06 / 0.20 in. labels of Fig. 2 (flow is
  drawn right to left, so the LE is at the 0.14 in. label).
- Flowpath (Fig. 2): constant hub 24 in. and tip 30 in.; axial stations
  X = -4.0 (screen/injector), 0.0 (Sta. 0), 9.0 (Sta. 1), 11.0 (hub step
  upstream of the rotor disk), 19.6 (Sta. 2, 0.3 Bx aft of the TE at
  midspan), 29.3 in. (Sta. 3). The rotor LE/TE axial positions are not
  dimensioned: from Sta. 2 at 19.6 in. and Bx = 5 in., the midspan TE is at
  about 18.1 in. and the LE at about 13.1 in. (interpretation, not printed).
- Stacking axis and section planes (cylindrical vs planar) are not stated.


## Pass B comparison (independent blind re-read, validation/pass_b/)

The two readings of the five coordinate tables differ in 9 cells, all the
dot-matrix 0/6/8 ambiguity. Each was decided by fitting a cubic through the
three neighbours on each side along the same surface: four are clear and are
written without '?'; five lie near the leading or trailing edge, where the fit
cannot separate the readings (differences of 0.0002 or less), and keep '?'.

| File | Row | Column | Before | After |
|---|---|---|---|---|
| CR3701_tableI_coords_span0.csv | X=3.22583 | Y PRES. | .82668 | .82668 |
| CR3701_tableI_coords_span0.csv | X=3.37702 | Y PRES. | .82466 | .82466 |
| CR3701_tableI_coords_span50.csv | X=.05008 | Y SUCT. | .07864 | .07884 |
| CR3701_tableI_coords_span75.csv | X=3.52827 | Y PRES. | .41390 | .41396 |
| CR3701_tableI_coords_span0.csv | X=-.00261 | Y PRES. | .00363 | .00363? |
| CR3701_tableI_coords_span0.csv | X=4.58655 | Y PRES. | .65383? | .65383? |
| CR3701_tableI_coords_span0.csv | X=5.93152 | Y PRES. | .01986 | .01966? |
| CR3701_tableI_coords_span25.csv | X=.11510 | Y PRES. | -.01233? | -.01233? |
| CR3701_tableI_coords_span50.csv | X=5.94973 | Y PRES. | -.00238 | -.00238? |
