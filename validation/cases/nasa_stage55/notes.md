# Stage 55-55 (NASA TM X-3101) - transcription notes

Source: Lewis and Tysl, *Overall and Blade-Element Performance of a
1.20-Pressure-Ratio Fan Stage at Design Blade Setting Angle*, NASA TM X-3101,
1974, NTRS 19740025117.

## Numbering
"rotor 55 and stator 55 (designated stage 55-55)" (pdf p4). No IGV. A
Hamilton Standard design (51-cm model of a 183-cm fan, variable-pitch rotor);
the design blade-element parameters "are those supplied by the contractor".
This report covers the design rotor setting angle only (the reset angles are
in its reference 1).

## What was transcribed
Tables I-V and the Fig. 1 flow-path box. No cell is marked '?'. All
blade-element rows pass velocity-triangle / Mach-ratio checks; geometry rows
pass TOTAL CAMBER = KIC - KOC. Measured performance (Table VI, all speeds;
Tables VII-VIII at 100 percent speed) added later: see "Measured performance"
below.

## Profiles
- Rotor: double circular arc (ZMC = ZTC, X FACTOR 1.000, DELTA INC 0, PHISS 0).
- Stator: "NACA 400 Series airfoils", constant chord (AERO CHORD 10.584 to
  10.589 cm). The report gives no further definition (no thickness-form
  designation, no camber-line type, no max-thickness location). From Table V:
  TI 0.188, TM 0.953, TO 0.087 cm on every row (TM/chord about 0.090), and
  (ZMC - ZI)/(ZO - ZI) is about 0.37 of the axial chord (derived, not stated).
  The table still reports KTC/ZTC (equal to ZMC); for this profile KTC is the
  camber-line angle at that point, not a MCA transition.
- AERO CHORD is defined here as the straight line between LE and TE "along
  design streamline" (appendix C), not on the cone.

## Clearance and contoured tip
- Rotor tips contoured for resetting to reverse pitch. Nominal tip clearance
  0.06 cm at the blade centerline, about 0.08 cm at LE and TE, at the design
  setting angle (pdf p5). Not stated whether cold or running; nothing else is
  given.
- Table IV rotor TIP RI = RO = 25.400; Fig. 1 tip radius 25.4 from z = 0 to 10
  and 25.6 at z = 15 (rotor TIP ZO = 6.522).

## Conventions
- Z referenced from rotor blade hub leading edge (appendix A, Fig. 1 axis);
  table columns ZI/ZMC/ZTC/ZO (appendix C says ZIC... "from inlet"). Rotor HUB
  ZI = 0.; rotor TIP ZI is negative (-0.636, swept forward at the tip).
- PERCENT SPAN from tip at rotor outlet; beta from axial; kappa to meridional
  plane. Rotor DELTA INC printed as 0./-0. (DCA).
- Stations 1-3: positions only drawn in Fig. 1 ("figure only"; no numbers
  printed).
- No part-span damper mentioned.

## Inconsistencies noticed
- Fig. 1 hub radius at z = 0 and 5 is 11.55 cm, but Table II/IV rotor HUB
  RI = RO = 11.684 cm. The figure box is coarse (2 decimals) and differs by
  0.13 cm; prefer the tables for the blade rows.
- Fig. 1 hub radius rises to 13.90 at z = 35 then falls (13.40, 13.00,
  12.50): a hub bump around the stator exit (consistent with the drawing,
  where the stator hub has a step). Stator HUB RI 12.548 / RO 13.818.
- Table II rotor HUB INCIDENCE MEAN 0.0 while other rows are negative; as
  printed.

## Measured performance (Tables VI-VIII)

Table VI (overall performance, pdf p24-25, printed 22-23), all five speed
parts; Table VII (rotor 55) parts (j)-(n), pdf p35-39, and Table VIII
(stator 55) parts (j)-(n), pdf p55-59, the five 100-percent-speed readings.
Rendered at 300 dpi; second read cell by cell at 600 dpi (suspect cells up
to 1200 dpi). Files: `TMX3101_tableVI_overall_<NNN>pct.csv` (readings as
columns), `TMX3101_tableVII_rotor55_reading<N>.csv`,
`TMX3101_tableVIII_stator55_reading<N>.csv`.

### Readings

| Speed | Table VI part | Readings (printed order) | Tables VII/VIII parts |
|---|---|---|---|
| 80 % | (a) | 1606, 1600, 1598, 1597 | (a)-(d), not transcribed |
| 90 % | (b) | 1604, 1596, 1595, 1594, 1588 | (e)-(i), not transcribed |
| 100 % | (c) | 1603, 1611, 1613, 1614, 1592 | (j)-(n), transcribed |
| 110 % | (d) | 1692, 1693, 1694 | (o)-(q), not transcribed |
| 120 % | (e) | 1697, 1696, 1695 | (r)-(t), not transcribed |

Table VI prints readings from high to low flow; Tables VII/VIII print one
part per reading, from low to high flow within each speed.

- Test procedure (pdf p6, printed 4): data "at 80, 90, 100, 110, and 120
  percent of design speed ... over a range of weight flow from maximum flow
  to the near-stall conditions. Data were recorded at nine radial positions".
- Peak efficiency (pdf p8, printed 6): stage peak efficiency 0.87 at design
  speed "at a measured equivalent weight flow of 26.7 kilograms per second
  (167 kg/sec/m2 of annulus area) and pressure ratio of 1.177", against design
  31.2 kg/sec and 1.196. This is reading 1613 (orifice 26.74, annulus 167.36,
  stage PR 1.177, stage eff 0.871). Rotor peak efficiency 0.92 "at an
  equivalent weight flow of 30.0 kilograms per second" is reading 1611
  (orifice 29.97, rotor eff 0.918). The peak-efficiency flow is about 14 %
  below design flow.
- Stall margin (pdf p8): "At design speed, the stall margin for the stage
  was 18 percent", from peak efficiency and "the values just prior to stall"
  (eq. B17, pdf p15). Stall flow was taken as the last flow before stall
  while closing the valve, and the stall pressure ratio was extrapolated from
  the survey data (pdf p7); the stall points are not tabulated. Evaluated from
  Table VI with 1613 as reference and the lowest-flow reading 1592 as stall,
  the margin is 17.8 % (orifice flow) or 17.9 % (rotor-inlet flow), matching
  the text.
- Design speed is about 8020 rpm (ROTATIVE SPEED / PERCENT OF DESIGN SPEED
  is 80.15-80.24 on every reading). Reading 1606 ran at 80.3 % while the other
  80 % readings ran at 78.3-78.5 %.

### Stations and averaging (pdf p6-7, printed 4-5)

- Three measuring stations (Fig. 1 positions only, no numbers); data
  "translated to planes approximating the blade leading and trailing edges"
  (reference 3 of the report). Tables VII/VIII are at the blade edges.
- Behind the stator, two combination probes traversed nine circumferential
  positions across the stator gap at each radius; total temperature
  mass-averaged and total pressure energy-averaged across the gap; flow
  angles from mass-averaged axial and tangential velocities. Overall values:
  radial total temperature mass-averaged, total pressure energy-averaged.
  Stations 1 and 2 recorded at one circumferential position only.
- Static pressure was not measured at 5, 10 and 95 percent span (wedge
  probe construction); it is interpolated linearly between the wall tap and
  the 15 or 90 percent span reading.
- Flows, pressures and temperatures corrected to sea-level conditions based
  on the rotor inlet. The estimated-error list (pdf p6) gives flow rate
  +/-0.3 kg/sec; the rest of the list is garbled in the text layer and was
  not transcribed.

### Format

- Table VI has no units row and no stator pressure- or temperature-ratio
  rows. Units from appendix C: WT FLOW kg/sec (equivalent), per-area flows
  kg/(sec)(m2), ROTATIVE SPEED rpm.
- Tables VII/VIII print RP 1-9 only (no TIP/HUB rows), INCIDENCE MEAN only
  (no SS column) and no PEAK SS MACH NO column. The stator tables print
  WHEEL SPEED and EFF as '0.'; both kept as printed. LOSS COEFF/PARAM PROF
  equal TOT on every row.

### Checks (a check never overrode a clear print)

- Every blade-element row: |V| and |W| from the meridional and tangential
  components (0.15 m/sec), absolute and relative angles (0.1 deg), meridional
  and relative Mach numbers from the absolute Mach number and the velocity
  ratios, MERID VEL R; rotor EFF from TOTAL PRESS/TEMP RATIO; stator LOSS
  COEFF TOT from the pressure ratio and inlet Mach number; stator absolute and
  relative columns identical. All 10 tables pass.
- Rotor outlet total pressure and temperature (inlet value times ratio)
  equal stator inlet values within the last printed digit at every RP and
  reading; radii and PERCENT SPAN identical across the five readings.
- Table VI: rotor and stage efficiency from the pressure and temperature
  ratios within the rounding of the 3-decimal temperature ratio; annulus- to
  frontal-area flow ratio 1.2684-1.2685 and orifice flow to frontal-area flow
  ratio 0.2027 on every reading; head-rise coefficient over
  (PR^(0.4/1.4) - 1) constant within each speed, scaling with 1/N^2.
