# NASA core compressor 74A (NASA TP-2597): transcription notes

Source: Steinke, R. J., *Design of 9.271-Pressure-Ratio Five-Stage Core Compressor
and Overall Performance for First Three Stages*, NASA TP-2597, May 1986, NTRS
19870008266. PDF page index = printed page + 2. Every page was rendered at 200 dpi
and read from the images. The pdftotext layer was used only to find pages.

## Scope: what the report gives for which rows

- **5 stages were designed. Only the IGV and the first 3 stages (the "inlet stage
  group", design PR 4.474, efficiency 0.799) were built and tested.**
- The report prints blade-element tables (Table IV) and blade geometry (Table V)
  **only for the IGV, rotors 1-3 and stators 1-3** (p9: "Tables IV and V list radial
  distributions of blade aerodynamic and geometric parameters for the inlet stage
  group (first three stages) of compressor 74A."). For stages 4 and 5 the report
  gives only Table I (aspect ratio, tip solidity, blade count), Table III (stage
  overall parameters) and the Figure 1 flowpath. Blade geometry for stages 4-5
  does not exist in this report.
- Test data are overall performance only (plenum inlet; outlet rakes 6.8 cm
  downstream of stator 3). There are no blade-element or interstage measurements.

## Files

| File | Content |
|---|---|
| `TP2597_fig1_flowpath_5stage.csv` | Tip and hub coordinates printed in Fig. 1 (5-stage machine) |
| `TP2597_fig2_flowpath_3stage.csv` | Same for Fig. 2 (3-stage test build, annulus changed downstream of stator 3) |
| `TP2597_tableI_blade_row_parameters.csv` | Table I, all 11 rows |
| `TP2597_tableII_overall.csv` | Table II: overall design parameters (3-stage group and full 74A) |
| `TP2597_tableIII_stage_parameters.csv` | Table III, IGV and stages 1-5 |
| `TP2597_tableIV_<row>.csv` | Table IV(a)-(g): igv, rotor1, stator1, rotor2, stator2, rotor3, stator3 |
| `TP2597_tableV_<row>.csv` | Table V(a)-(g): same rows |
| `TP2597_tableVI_mechanical.csv` | Table VI: stress factor of safety and flutter parameters |
| `TP2597_fig18_design_settings.csv` | Inset of Fig. 18: design IGV/stator settings (all 0) |
| `TP2597_fig21_reset_schedule.csv` | Inset of Fig. 21: reset applied at all speeds |
| `TP2597_fig22_reset_schedule.csv` | Inset of Fig. 22: reset schedule for each speed |

Table II is "DESIGN OVERALL PERFORMANCE PARAMETERS FOR CORE COMPRESSOR 74A". It
is a two-column overall-design table (first three stages vs. compressor 74A):
PR, TR, adiabatic and polytropic efficiency, specific flow, mass flow, speed and
tip speed. It is transcribed.

## CSV conventions used

- Tables IV and V are printed as stacked blocks: four for Table IV, three for
  Table V. Each blade row's blocks are merged into one CSV, one line per RP
  (TIP, 1-11, HUB). Headings are "<group heading> <sub heading>" as printed.
  Table IV headings: `RADII IN/OUT`, `ABS BETAM IN/OUT`, `REL BETAM IN/OUT`,
  `TOTAL TEMP IN/RATIO`, `TOTAL PRESS IN/RATIO`, `ABS VEL`, `REL VEL`, `MERID VEL`,
  `TANG VEL`, `WHEEL SPEED`, `ABS MACH NO`, `REL MACH NO`, `MERID MACH NO`,
  `STREAMLINE SLOPE IN/OUT`, `MERID VEL R`, `PEAK SS MACH NO`, `PERCENT SPAN`,
  `INCIDENCE MEAN/SS`, `DEV`, `D-FACT`, `EFF`, `LOSS COEFF TOT/PROF`,
  `LOSS PARAM TOT/PROF`. Table V headings: `PERCENT SPAN`, `RADII RI/RO`,
  `BLADE ANGLES KIC/KTC/KOC`, `DELTA INC`, `CONE ANGLE`, `BLADE THICKNESSES
  TI/TM/TO`, `AXIAL DIMENSIONS ZI/ZMC/ZTC/ZO`, `AERO CHORD`, `SETTING ANGLE`,
  `TOTAL CAMBER`, `SOLIDITY`, `TURNING RATIO`, `PHISS`, `CHOKE MARGIN`.
- Row 2 (units) is blank in the Table IV/V CSVs because no units are printed in
  those tables. Units from Appendix C (p17): radii, thicknesses, Z values and
  AERO CHORD in cm; velocities and wheel speed in m/sec; TEMP in K; PRESS in
  N/cm^2; all angles in deg (BETAM, KIC/KTC/KOC, INCIDENCE, DELTA INC, DEV,
  PHISS, STREAMLINE SLOPE, CONE ANGLE, SETTING ANGLE, TOTAL CAMBER).
- Values are copied exactly as printed: `.0`, `-.0`, `-.00`, `0.` (PERCENT SPAN
  in Table V), `.00` (PERCENT SPAN in Table IV), `16 042.300` (space as thousands
  separator), `+ 8` (space inside the reset-schedule cells).
- The flowpath boxes print units inside the heading ("Tip axial coordinates,
  cm"). The heading is given without ", cm" and `cm` goes in the units row.
- The units of the reset-schedule insets are not printed. The text (p13) gives
  degrees ("resetting the IGV's +15° and each stator blade row +10°").

## Conventions stated in the report

- **Blade elements** lie on conical surfaces through the streamline locations
  (Fig. 9). Each element is two segments with a constant rate of angle change
  (C1, C2). MCA when C1 ≠ C2. DCA when C1 = C2 and the maximum thickness is at
  midchord. All blades are thickest at midchord.
- **Angles** KIC/KTC/KOC and SETTING ANGLE are measured from the meridional
  plane, on the conical surface. TOTAL CAMBER = KIC-KOC. BETAM is the
  meridional air angle. CONE ANGLE is the angle between the axial direction and
  the element's conical surface. Stator rows print positive REL BETAM IN equal
  to ABS BETAM IN, and negative KOC (overturning past axial). Rotor and stator
  angles are therefore each given in their own sense; the report does not state
  the sign convention in words.
- **Z (ZI, ZMC, ZTC, ZO)** is defined only as "axial distance to blade leading
  edge" etc. **The origin is not stated.** Observation only, not from the text:
  rotor 1 HUB ZI is printed `-.000`, and the flowpath boxes use the same axis
  (the hub point near 0 is `-.033`). This suggests the origin is the rotor 1 hub
  leading edge. The IGV Z values are negative.
- **PERCENT SPAN** (Appendix C): "percent of blade span from tip reference to
  rotor one outlet". As printed; TIP = 0, HUB = 100.
- **DELTA INC** = mean-camber angle minus suction-surface angle at LE. It is
  consistent with INCIDENCE MEAN − INCIDENCE SS to within about 0.1 deg.
- **Stacking**: about the centres of area along a prescribed stacking line.
  Fabrication coordinates are on planes perpendicular to a radial line through
  the hub stacking point. Fabrication coordinates are **not** printed in this
  report.
- **Profiles (p8)**: "Blades having low inlet relative Mach numbers (all stators
  and rotor 3), were of double circular arc (DCA) shape. Blades having supersonic
  inlet relative Mach numbers (the midspan to tip regions of rotors 1 and 2) were
  of multiple circular arc (MCA) shape." No exact span limit is given in the text.
  Observation from Table V: TURNING RATIO < 1 appears in rotor 1 at RP TIP-9
  (0-80 %; RP 10 = 1.002) and in rotor 2 at RP TIP-8 (0-70 %; RP 9 = 1.001). Values
  of .9xx near 50-70 % span mean the MCA extends somewhat below midspan.
- **IGV**: zero camber (KIC = KTC = KOC = TOTAL CAMBER = .00 at every RP), zero
  design incidence and deviation, a radially constant 2 % total-pressure loss,
  and a variable setting. SETTING ANGLE is printed `-.29` at every RP. The edge
  thicknesses differ (TI .123-.128 vs TO .062-.064 cm), so the vane is
  symmetric about its camber line but **not fore-aft symmetric**.
- **Variable rows**: the IGV and stators 1-3 (reset schedules in Figs. 18, 21
  and 22). The positive reset direction is shown only graphically in Fig. 20.
- **Clearances: not stated anywhere** (no tip or hub clearance, cold or running,
  in the text, figures, tables or appendixes).
- Measurement stations: inlet in the plenum (two thermocouples; four wall statics
  ~90° apart). Outlet: four rakes ~90° apart, 6.8 cm downstream of the stator 3
  row, with elements at 10/30/50/70/90 % span from the outer casing. The axial
  position of the rakes in Z coordinates is not given.

## Cells marked `?` (best reading, glyph damaged in the print)

| File | RP | Column | Reading | Why |
|---|---|---|---|---|
| tableIV_igv | 7 | REL MACH NO IN | `.498?` | middle digit broken; ABS and MERID values in the same row are .498 |
| tableIV_igv | 10 | EFF | `.000?` | last glyph broken (looks like `.00J`) |
| tableIV_rotor1 | 1 | REL VEL IN | `461.2?` | second digit partly missing (6 vs 4); velocity triangle gives 461.1 |
| tableIV_stator1 | 2 | PEAK SS MACH NO | `1.128?` | third digit smudged |
| tableIV_rotor2 | 3 | WHEEL SPEED IN | `386.8?` | last digit printed like `R` |
| tableIV_rotor2 | HUB | WHEEL SPEED IN | `277.0?` | last digit broken |
| tableIV_stator2 | 7 | D-FACT | `.503?` | last digit broken |
| tableIV_stator3 | 1 | ABS VEL OUT | `187.2?` | last digit broken; REL VEL OUT and MERID VEL OUT print 187.2 |
| tableIV_stator3 | 3 | INCIDENCE MEAN | `5.0?` | last digit printed like `G` |
| tableV_igv | 6 | AXIAL DIMENSIONS ZI | `-7.198?` | digit broken (`-7.1?8`) |
| tableV_igv | 8 | AXIAL DIMENSIONS ZI | `-7.208?` | digit broken (`-7.2?8`) |
| tableV_igv | 8 | AXIAL DIMENSIONS ZTC | `-4.130?` | last digit broken |
| tableV_igv | 2 | SETTING ANGLE | `-.29?` | last digit broken; all other RPs print -.29 |
| tableV_igv | 5 | TOTAL CAMBER | `.00?` | digits smudged |
| tableV_igv | 8 | SOLIDITY | `1.588?` | second digit broken |
| tableV_rotor1 | 8 | AXIAL DIMENSIONS ZMC | `3.471?` | last digit broken |

## Printed values that fail a plausibility check (copied as printed, not changed)

- **tableIV_rotor3, RP 1, EFF = `.685`**: printed clearly. The neighbours are
  .869 (TIP) and .891 (RP 2), so `.885` was probably intended.
- Table IV rotors: INCIDENCE MEAN and DEV differ from (REL BETAM − KIC/KOC of
  Table V) by up to about 0.1-0.3 deg (e.g. rotor 1 HUB: 48.4 − 42.43 = 5.97 vs
  printed 6.2). This is probably because the printed flow angles are rounded and
  the cone-surface angles are not exactly the meridional ones. Not a reading
  issue.
- Table I IGV tip solidity 1.00 vs Table V(a) TIP SOLIDITY .992; rotor 1 tip
  1.35 vs Table V 1.336. Table I values are rounded or nominal.
- Hub coordinate at x = 35.745 (Fig. 1) vs 35.746 (Fig. 2): both as printed.
- The Fig. 22 schedule includes a 50 % speed row, but the text (p11) says data
  were recorded at 60-100 % (Figs. 21 and 22 do show a 50 % line).
- The Table IV(a) subtitle reads "Inlet guide wave" (typo in print). Table V(a)
  reads "Inlet guide vane".
- Rotor 1 HUB ZI is printed `-.000` (negative zero), copied as printed.

## Figure only (no tabulated numbers; not digitised)

Fig. 3 (stator 3 TE static pressures), Fig. 4 (total blockage factors), Fig. 5
(stage energy fraction), Figs. 6-8 (loss and shock-loss correlations), Fig. 9
(conical coordinate system), Fig. 10 (blade-element layout parameters), Fig. 11
(wave pattern), Fig. 12 (deviation adjustment factors added to Carter's rule),
Fig. 13 (rotor turning rate ratio vs span; the same data are tabulated as
TURNING RATIO in Table V), Fig. 14 (rotor choke margin; tabulated in Table V),
Fig. 15 (Goodman diagrams), Fig. 16 (Campbell diagrams), Fig. 17 (test
facility), Fig. 19 (rotor 1 exit tip static pressure, test vs Denton code), Fig.
20 (reset sign schematic), and the performance maps in Figs. 18, 21 and 22 (the
plotted test data are not digitised; only their inset setting tables are
transcribed).

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 15, still '?' 1, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP2597_tableIV_igv.csv | 10 | REL MACH NO IN | `.498?` | `.498` | IGV (U = 0): REL MACH IN = ABS MACH IN = MERID MACH IN = .498 | 600-dpi read: middle digit broken (.4?8); exact relation fixes .498 |
| TP2597_tableIV_igv.csv | 13 | EFF | `.000?` | `.000` | IGV EFF printed .000 on every other row | 600-dpi read: last 0 open (dropout); value .000 |
| TP2597_tableIV_rotor1.csv | 4 | REL VEL IN | `461.2?` | `461.2` | W = sqrt(VM^2 + U^2) with VTH = 0: sqrt(188.4^2 + 420.9^2) = 461.14, range 461.07-461.21 over input rounding; W/V = M'/M gives 461.6 +- 0.6; 441.2 excluded | 600-dpi zoom: second glyph is a 6 with its lower loop broken (curved top stroke, not the angular 4); .2 clear |
| TP2597_tableIV_rotor2.csv | 6 | WHEEL SPEED IN | `386.8?` | `386.8` | U = omega r with omega from rows TIP and 4 (416.3/24.778, 373.0/22.201 = 16.801 /s per cm): 23.025 x 16.801 = 386.84 | 600-dpi zoom: last glyph has the closed upper loop and the lower-left stroke of an 8 (a 9 has no lower-left stroke); relation agrees |
| TP2597_tableIV_rotor2.csv | 15 | WHEEL SPEED IN | `277.0?` | `277.0` | U = omega r: 16.487 x 16.801 = 277.00 | 600-dpi zoom: last glyph is an open 0 (dropout, G-like); relation agrees |
| TP2597_tableIV_stator1.csv | 5 | PEAK SS MACH NO | `1.128?` | `1.128?` | no independent relation for PEAK SS MACH NO; neighbours 1.130 and 1.140 admit 1.128 or 1.138 | 600-dpi zoom: third digit is a smudged glyph with a 2/3-like top; still uncertain, kept |
| TP2597_tableIV_stator2.csv | 10 | D-FACT | `.503?` | `.503` | Lieblein D = 1 - V2/V1 + (r1 VTH1 - r2 VTH2)/((r1+r2) sigma V1) = 1 - 193.9/261.6 + 20.196 x 182.7/(40.708 x 1.417 x 261.6) = 0.5033 (formula reproduces row 6 .497) | 600-dpi read: .503 with the 3 slightly broken; relation agrees |
| TP2597_tableIV_stator3.csv | 4 | ABS VEL OUT | `187.2?` | `187.2` | stator: ABS VEL OUT = REL VEL OUT = MERID VEL OUT = 187.2 (TANG VEL OUT .0) | 600-dpi read: last digit broken; exact relation fixes 187.2 |
| TP2597_tableIV_stator3.csv | 6 | INCIDENCE MEAN | `5.0?` | `5.0` | INCIDENCE MEAN = ABS BETAM IN - KIC = 42.6 - 37.54 = 5.06 (range 5.01-5.11; formula gives 5.61 vs printed 5.6 on row 1) | 600-dpi read: last glyph is round with a gap (0 or 6); 5.6 excluded by the relation, so 5.0 |
| TP2597_tableV_igv.csv | 5 | SETTING ANGLE | `-.29?` | `-.29` | IGV setting angle printed -.29 on all other 12 rows (uniform IGV restagger) | 600-dpi read: -.2 clear, 9 with broken tail; value -.29 |
| TP2597_tableV_igv.csv | 8 | TOTAL CAMBER | `.00?` | `.00` | TOTAL CAMBER = KIC - KOC = .00 - .00 (IGV is uncambered) | 600-dpi read: smudged .00; exact relation fixes .00 |
| TP2597_tableV_igv.csv | 9 | AXIAL DIMENSIONS ZI | `-7.198?` | `-7.198` | ZO - CHORD cos(CONE ANGLE) = -1.041 - 6.178 cos 4.730 = -7.1979; also ZMC - 0.4 CHORD cos(CONE) = -7.1978 (both relations reproduce rows 7 and TIP to 0.001) | 600-dpi zoom: -7.1?8 with a broken 9; relations agree |
| TP2597_tableV_igv.csv | 11 | AXIAL DIMENSIONS ZI | `-7.208?` | `-7.208` | ZMC - 0.4 CHORD cos(CONE) = -4.746 - 0.4 x 6.215 cos 7.951 = -7.2081 | 600-dpi zoom: -7.2?8 with a broken 0 (C-like); relation agrees |
| TP2597_tableV_igv.csv | 11 | AXIAL DIMENSIONS ZTC | `-4.130?` | `-4.130` | ZTC at mid chord: ZO - 0.5 CHORD cos(CONE) = -4.1297 and ZI + 0.5 CHORD cos(CONE) = -4.1303 (relation reproduces TIP and row 9 exactly); -4.139 excluded | 600-dpi zoom: last glyph broken (9- or 0-like); relations fix -4.130 |
| TP2597_tableV_igv.csv | 11 | SOLIDITY | `1.588?` | `1.588` | solidity = N c/(2 pi r_mean) = 26 x 6.215/(2 pi x 16.1935) = 1.5882 (row 9 gives 1.7688 vs 1.769) | 600-dpi read: second digit broken (1.?88); relation agrees |
| TP2597_tableV_rotor1.csv | 11 | AXIAL DIMENSIONS ZMC | `3.471?` | `3.471` | no exact relation; (ZMC-ZI)/(ZO-ZI) = 0.4599 lies on the smooth radial trend (0.4620, -, 0.4591) | 600-dpi zoom: last glyph is a 1 with a gap in the stem (flag and stem visible); reading 3.471 |
