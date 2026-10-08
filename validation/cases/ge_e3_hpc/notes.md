# GE/NASA E3 10-stage high-pressure compressor

Sources: NASA CR-165558 (detail design report: Table XXI original-design vector diagrams and airfoil
geometry, Table XXII final-design airfoil geometry, design text, Table XVI clearance elements) and NASA
CR-168245 (component performance report: builds, VSV schedules, maps, traverses; used here only for
scalars and pointers). See source.json and scalars.json. CR-165558 printed page = pdf page - 9;
CR-168245 printed page = pdf page - 10. All page numbers below are pdf pages unless marked "printed".

## What is transcribed

| Item | Files | Pages (pdf) | State |
|---|---|---|---|
| Table XXI, original-design blading, SI pages: IGV, Rotors 1-10, Stators 1-10, four blocks per row (INLET, EXIT, SL DATA, PLANE SECTIONS) | `CR165558_tableXXI_<row>_{inlet,exit,sldata,planesections}.csv` (84 files) | 121-141 (U.S.-unit facing pages 142-162, used as cross-check) | Complete. IGV-S9 transcribed by an earlier session and second-read here; S10 (p141) transcribed and second-read here. |
| Table XXII, final-design blading, plane sections only (SI with inches in parentheses) | `CR165558_tableXXII_<row>.csv` (21 files: R1-R10, IGV, S1-S10) | 163-168 | Complete, new in this session, second read done. |
| Single values (blade counts, design point, bleeds, VSVs, profiles, clearance elements, definitions) | `scalars.json` | various | Done. |

Row order of Table XXI pages: IGV 121, R1 122, S1 123, R2 124, R3 125, S2 126, S3 127, R4 128, S4 129,
R5 130, S5 131, R6 132, S6 133, R7 134, S7 135, R8 136, S8 137, R9 138, S9 139, R10 140, S10 141 (note
R3 precedes S2 in the binding). U.S. facing pages: same order on 142-162, except S2 is on 146 and R3 on 147.
There is no separate OGV row: Stator 10 is the outlet guide vane ("Campbell diagrams for IGV through
Stage 10 (OGV)", p89; Table XV p105 lists "OGV" after Stage 9). Table XXII has no vector diagrams
(plane sections only); Table XXI has no flowpath table beyond the hub/tip rows (SL1 = casing,
SL12 = hub) at each blade edge.

Not transcribed (figure only): CR-165558 Fig. 9 (core compressor cross section, p28), Fig. 15 (CAFD
flowpath and streamlines), Fig. 61 and 62 (clearances by stage, p109-110), Fig. 60 (10A rig bleeds,
p107). CR-168245 figures listed below.

## Blade counts

From the page headers of Table XXI and the block labels of Table XXII (scalars.json `blade_count_*`):
IGV 32, R1 28, S1 50, R2 38, R3 50, S2 68, R4 60, S3 82, S4 92, R5 70, S5 110, R6 80, S6 120, R7 82,
S7 112, R8 84, S8 104, R9 88, S9 118, R10 96, S10 140 (original design). Final design (Table XXII):
identical except R9 86 and R10 94. Stator 7 in Table XXII is labelled "112 VANES*"; no footnote for the
asterisk exists in the scan (p163-169 checked; p169 is the film end frame). Table VIII's "Number of
Rotors and Stators 1672" equals the original-design R1-R10 + S1-S10 total without the IGV.
The pdftotext layer reads the IGV header as "37 VANES"; the image prints 32 on both the SI and U.S. pages.

## Conventions stated in the report

- Nomenclature (p118-120, printed 109-111): `% IMM` percent immersion from the outer wall (SL1 = casing,
  SL12 = hub); `RADIUS` streamline radius; `Z` axial dimension; `R-BAR` average streamline radius based
  on the streamline radii at the blade edges (= mean of inlet and exit RADIUS of the same SL, checked);
  `SECT. HT.` height of plane sections from the compressor centerline (equals R-BAR of the same SL,
  checked; a few printed 0.001 differences are kept as printed).
- Units are not printed in the tables. From the nomenclature: lengths cm (in.), velocities `U`, `CZ`
  m/sec (ft/sec), angles deg. `PT/PTI`, `TT/TTI` are streamline absolute total pressure / temperature
  divided by the compressor-inlet average (inlet average set at standard-day sea-level static, p38),
  so values above 1 are cumulative ratios (e.g. 25.33 at S10 inlet).
- `BETA` relative flow angle = arctan(-Wu/Cz); `ALPHA` absolute flow angle = arctan(Cu/Cz); `PHI`
  meridional flow angle (sign not defined in the text; in the tables it is negative near the casing
  where the annulus converges, i.e. positive = radially outward flow). `INC`, `DEV` are defined
  "in cascade projection"; `CHORD`, `CAMBER`, `STAGGER` (angle between blade chord and axial direction),
  `BETA1*`, `BETA2*` (angle between camber-line tangent and axial direction at LE / TE), `TM/C`,
  `%C TM`, `TTE/C` are "in a plane section normal to (blade) stacking axis". Rotor and stator angles
  are both given as positive numbers in their own frame (rotor BETA and stator ALPHA both about +40 to
  +65 deg at inlet); the sign convention relative to rotation is not stated beyond the arctan definitions.
- IGV blocks print `CLO` (design lift coefficient, Dunavant correlation) instead of camber and metal angles.
- Plane sections: "The bottom row, labeled "Plane Sections," provides a description of the airfoil
  geometry on flat plane manufacturing sections. These sections are generally located at the average
  radius of a calculated streamline, and thus part of the first and last sections may be outside the
  flowpath." (p38). They are planes normal to the stacking axis, not cones or cylinders, and sit at
  SECT. HT. = R-BAR. The stacking-axis location and orientation are not tabulated.
- Stations: "The stations defined by the "radius" and "Z" columns lie along the blade edges at both
  inlet and exit. The hub coordinates are for the smoothed-out aerodynamic representation of the actual
  hardware." (p38). The real hub has 2-3 deg tilted shrouds/platforms (p38, scalars `hub_tilt`).
- Z origin: not stated in words. In the tables Z = -0.000 at the Rotor 1 inlet hub (R1 inlet SL12),
  the IGV is at negative Z (-7.658 to -1.458) and S10 exit is at Z = 78.207 cm, so Z is measured
  axially from the Rotor 1 hub leading edge, positive downstream. Every exit plane has a separate Z per
  SL (blade edges are not radial lines); S10 exit has constant Z.
- Signs in the scan: the SI pages often lose minus signs and decimal points (the decimal position is
  fixed per column and was restored). Where a minus sign is missing on the SI page, the U.S. page
  (angles are unit-independent) was used. Two second-read workers applied slightly different rules:
  for R3, S2, S3, R4, S8, R9, S9, R10 a minus taken only from the U.S. page carries `?`; for IGV-S1-R2,
  S4-R6, S6-R8 and S10 a minus clearly printed on the U.S. page (or confirmed by CAMBER = BETA1* -
  BETA2*) is written without `?`. Where neither page prints a minus but the radial trend suggests one,
  the value is written unsigned with `?` (e.g. R4 exit PHI SL1 4.84?, R5 inlet PHI SL1 4.84?): these
  are probably negative.
- Cells converted from the U.S. page because the SI digits are illegible (always with `?`): R3 exit U
  SL8, S2 exit CZ SL4, R4 inlet CZ SL2, R5 inlet CZ SL12, R7 exit CZ SL3, S7 inlet Z SL8, R10 inlet Z
  SL8, R10 exit U SL4.

## Which build used which blading (CR-165558 p59-63, CR-168245 p57-58)

| Row | Six-stage rig (1-6, 1980) | First 10-stage (10A, 1981) | Second 10-stage (10B, 1981-82) | Final (core/ICLS engine) |
|---|---|---|---|---|
| IGV | Table XXI | interim: "The 4° open hub twist in the IGV row was also used" | same as 10A ("twisting open the IGV hub") | Table XXII |
| R1 | Table XXI | "2.5° tip closure in the first rotor" | "the twisted first rotor" | Table XXII (restaggered closed 2.5° at the tip) |
| R2 | Table XXI | Table XXI | "original design second rotor" | Table XXII (differs from XXI only at the two hub sections, BETA2* -0.18/-0.06) |
| R3-R6 | Table XXI | Table XXI ("the other front block rotors were unchanged") | redesigned high-hub-camber rotors = Table XXII | Table XXII |
| R7 | (not in rig) | Table XXI ("Rotor 7 retained its original design") | Table XXII (high hub camber) | Table XXII |
| S1-S4 | Table XXI | interim, not tabulated: "twisted open 3.5° at the hub ... 8° more camber in the hub of Stators 1 through 4" | CR-168245 p57: S1 keeps the twist/hub camber; "the modified Stators 2 through 5 used in the previous build were reworked back to their original design geometry" | Table XXII |
| S5-S6 | Table XXI | interim, not tabulated: 3.5° hub open twist + "5° more camber in Stators 5 through 6" | S5 original; S6 keeps twist/hub camber (CR-168245 p57) | Table XXII |
| S7-S10 | (not in rig) | Table XXI ("the Stage 7 through 10 stator vanes were the original design") | Table XXI | Table XXII (S7-S9 redesigned with about 6.5° more hub TE camber; S10 unchanged) |
| R8-R10 | (not in rig) | alternate design "that had approximately 6° more camber at all radii": **not tabulated in either table** | Table XXI ("original design (lower camber) Rotors 8 through 10") | Table XXII = Table XXI staggered closed 2.00° at all radii (same airfoils) |

Notes on the table:
- CR-165558 p62 calls the 10B front stages "the final configurations as specified after the six-stage
  test (modified rotors and original stators), and whose geometry is tabulated in Table XXII". CR-168245
  p57 is more specific: IGV hub twist, S1 and S6 twist/hub camber and R1 tip closure carried over from
  10A; S2-S5 reworked to original. CR-165558 p89: "the core IGV, S1, and S6 airfoils have been
  restaggered 3.5° to 4.0° and recambered 5° to 8° from the 1-6 rig design. Stator 2 through 5 airfoils
  have been changed from the 1-10 rig design." Table XXII agrees: IGV, S1, S6 differ from Table XXI;
  S2, S5, S10 are identical; S3 and S4 differ only in one doubtful chord digit each and S3's printed
  camber typo (row 10 31.35). So for 10B: IGV, R1, S1, S6, R3-R7 from Table XXII; R2, S2-S5 effectively
  Table XXI = XXII; S7-S10 and R8-R10 from Table XXI. Whether the 10B S1/S6 hardware is exactly the
  Table XXII geometry (it was made for 10A as an interim fix) is not stated.
- The 10A interim stator modifications and the 10A high-camber R8-R10 are described only in words; a
  10A model needs geometry that is not printed.
- Final rotor differences (Table XXII minus Table XXI): R1 stagger/BETA1*/BETA2* +2.5 deg over the
  outer five sections, tapering to about 0 at the hub, camber +0.1 to +1.1 near the hub; R3 broad
  redesign (chord now about 5.05 cm constant, hub camber +5.7); R4-R7 hub camber +6 to +8.8 with hub
  stagger -2 to -3; R8-R10 stagger, BETA1*, BETA2* exactly +2.00, everything else identical.
- Final stator differences: IGV stagger only (8.03 -> 8.04 tip, 1.01 -> -3.00 hub, about 4 deg open at
  the hub); S1 and S6 camber/stagger/metal angles and chord; S7-S9 camber +4 to +5.6, metal angles,
  TM/C, TTE/C and (S8, S9) chord.
- The off-design estimate for the final configuration expects vector diagrams "very close to the
  original design intent, as listed in the Appendix (Table XXI)" at 23:1 near 100% speed (p63).

## Variable vanes, bleeds, clearances

- Design: "The inlet guide vane and first four stator vane rows are variable." (p28). Rigs: IGV and
  Stators 1 through 6 variable (CR-168245 p68; CR-165558 p58 "front six variable-stator stages").
- Design vector diagrams include 1.3% fifth-stage and 2.3% seventh-stage bleed (p38), extracted aft of
  Stators 5 and 7. Zero customer bleed at Stator 5 exit in the design calculations (p29).
- Clearances: only Table XVI (elements; rub allowance 0.013 cm, stall allowance 0.025 cm Stage 1 only)
  and Figs. 61-62 (plots, mm and mils, not digitized). CR-168245 p163: ACC closure 0.076 mm
  (touchprobe) / 0.152 mm (clearanceometer, R10) vs 0.127 mm predicted at 100% Nc, T25 = 211 K,
  P25 = 31.7 kPa. No tabulated cold or running tip clearance per rotor exists in either report;
  stator hub (shrouded) seal clearances are not given.

## CR-168245 (performance report): where the build data are (figure only unless stated)

pdf page (printed = pdf - 10). Located from page thumbnails and captions:
- Six-stage rig: Fig. 9 performance map p51; Fig. 10 "Compressor Six-Stage Test Stator Schedule" p52
  (stator setting angle deg vs percent corrected speed, IGV and S1-S6); Fig. 11 radial total-pressure
  profiles p55; Table I comparison of efficiencies p53.
- First 10-stage build (10A): Fig. 12 performance map p59; Fig. 13 stator schedule p61; Table II high
  speed efficiency summary p62; Fig. 14 map of Stages 7-10 p64; Fig. 15 map of Stages 1-6 p65; Fig. 16
  radial total-pressure distribution p66.
- Second 10-stage build (10B): build description p67-68; Fig. 17 performance map p70; Fig. 18 stator
  schedule p71; Table III maximum cruise efficiency p73; Fig. 19 front-block map p75; Fig. 20 rear-block
  map p77; Figs. 21-22 traverse data p78-79; Fig. 23 p80 (radial distribution, second build); inlet
  distortion Figs. 24-26 p82-85.
- Appendix "Compressor Performance Summary of the Second Ten-Stage Test": tabular, pdf 167 (title) and
  168-170 (tables). Not transcribed here; it is the only tabulated test data.
- 10B test conditions (p68): inlet refrigerated to about 200 K above 85% speed, inlet pressure about
  0.25 atm near design corrected airflow.

## Cells marked '?'

Every cell carrying `?`, with its column. Reasons are in source.json notes per file and summarised
above; in short: a broken or missing glyph that admits more than one digit, a minus sign not printed
on the SI page, a value converted from the U.S. page, or an SI/U.S. disagreement where the SI value is
kept. Row = SL number for Table XXI inlet/exit/sldata files, otherwise the printed row (1 = tip).

```
XXII_IGV.csv row 1 (CHORD) 2.466?
XXII_R1.csv row 7 BETA2* 43.82?
XXII_R10.csv row 11 STAGGER 48.63?
XXII_R3.csv row 9 BETA1* 53.07?
XXII_R3.csv row 11 TTE/C 0.0116?
XXII_R5.csv row 6 TTE/C 0.0128?
XXII_R5.csv row 12 BETA1* 52.98?
XXII_R6.csv row 4 BETA1* 60.71?
XXII_R7.csv row 4 CAMBER 19.53?
XXII_R8.csv row 11 TTE/C 0.0147?
XXII_R9.csv row 8 (SECT. HT.) 11.107?
XXII_R9.csv row 9 SECT. HT. 27.985?
XXII_S1.csv row 11 BETA2* -2.89?
XXII_S10.csv row 4 BETA1* 49.58?
XXII_S10.csv row 12 (SECT. HT.) 10.773?
XXII_S10.csv row 12 BETA1* 62.58?
XXII_S3.csv row 12 CHORD 2.8194?
XXII_S4.csv row 8 (SECT. HT.) 11.217?
XXII_S4.csv row 9 CHORD 2.4891?
XXII_S5.csv row 7 SECT. HT. 28.883?
XXII_S5.csv row 8 SECT. HT. 28.487?
XXII_S5.csv row 8 CAMBER 36.22?
XXII_S6.csv row 3 SECT. HT. 30.071?
XXII_S6.csv row 4 SECT. HT. 29.732?
XXII_S7.csv row 1 (SECT. HT.) 11.871?
XXII_S8.csv row 2 STAGGER 33.99?
XXII_S8.csv row 5 BETA1* 49.17?
XXII_S8.csv row 7 STAGGER 24.93?
XXII_S8.csv row 8 STAGGER 24.54?
XXII_S8.csv row 11 STAGGER 27.61?
XXII_S8.csv row 12 TTE/C 0.0141?
XXII_S9.csv row 1 (CHORD) 0.912?
XXII_S9.csv row 4 BETA1* 53.15?
XXII_S9.csv row 5 CHORD 2.1585?
XXII_S9.csv row 5 (CHORD) 0.850?
XXII_S9.csv row 5 TTE/C 0.0121?
XXII_S9.csv row 10 BETA1* 53.65?
XXI_R10_exit.csv row 1 PHI -2.52?
XXI_R10_exit.csv row 2 PHI -2.74?
XXI_R10_exit.csv row 3 PHI -2.78?
XXI_R10_exit.csv row 4 U 372.3?
XXI_R10_exit.csv row 4 PHI -2.45?
XXI_R10_exit.csv row 5 PHI -1.95?
XXI_R10_exit.csv row 6 PHI -1.39?
XXI_R10_exit.csv row 8 PHI -0.40?
XXI_R10_inlet.csv row 1 PHI -2.52?
XXI_R10_inlet.csv row 2 PHI 2.83?
XXI_R10_inlet.csv row 3 PHI -2.94?
XXI_R10_inlet.csv row 4 PHI -2.63?
XXI_R10_inlet.csv row 5 PHI -2.12?
XXI_R10_inlet.csv row 6 PHI -1.55?
XXI_R10_inlet.csv row 7 PHI -0.99?
XXI_R10_inlet.csv row 8 Z 73.479?
XXI_R10_inlet.csv row 8 PHI -0.47?
XXI_R10_inlet.csv row 9 PHI -0.01?
XXI_R10_planesections.csv row 1 BETA1* 66.48?
XXI_R10_sldata.csv row 7 LOSS 0.0553?
XXI_R10_sldata.csv row 10 INC -0.62?
XXI_R10_sldata.csv row 11 INC -1.35?
XXI_R10_sldata.csv row 12 INC -2.00?
XXI_R1_exit.csv row 11 RADIUS 21.232?
XXI_R1_exit.csv row 12 RADIUS 20.343?
XXI_R1_inlet.csv row 11 M-ABS 0.484?
XXI_R1_sldata.csv row 2 INC 3.20?
XXI_R2_exit.csv row 9 M-REL 0.621?
XXI_R2_exit.csv row 12 M-ABS 0.785?
XXI_R2_planesections.csv row 10 CHORD 6.7282?
XXI_R2_sldata.csv row 7 R-BAR 27.917?
XXI_R3_exit.csv row 4 PHI -2.62?
XXI_R3_exit.csv row 5 PHI -0.82?
XXI_R3_exit.csv row 8 U 361.7?
XXI_R3_inlet.csv row 2 PHI -3.58?
XXI_R3_inlet.csv row 3 PT/PTI 2.6204?
XXI_R3_inlet.csv row 3 PHI -2.25?
XXI_R3_inlet.csv row 4 PHI -0.61?
XXI_R3_inlet.csv row 10 TT/TTI 1.3756?
XXI_R3_inlet.csv row 11 TT/TTI 1.3975?
XXI_R3_planesections.csv row 3 CAMBER 10.92?
XXI_R3_sldata.csv row 1 INC 1.00?
XXI_R4_exit.csv row 1 PHI 4.84?
XXI_R4_exit.csv row 11 RADIUS 26.799?
XXI_R4_inlet.csv row 2 CZ 173.2?
XXI_R4_sldata.csv row 5 DF 0.4425?
XXI_R5_exit.csv row 11 M-ABS 0.644?
XXI_R5_exit.csv row 12 M-ABS 0.650?
XXI_R5_inlet.csv row 1 PHI 4.84?
XXI_R5_inlet.csv row 5 PHI 2.55?
XXI_R5_inlet.csv row 10 M-ABS 0.484?
XXI_R5_inlet.csv row 11 CZ 194.2?
XXI_R5_inlet.csv row 12 CZ 189.1?
XXI_R5_sldata.csv row 7 LOSS 0.0433?
XXI_R6_exit.csv row 1 PT/PTI 9.8070?
XXI_R6_exit.csv row 5 TT/TTI 2.0194?
XXI_R6_exit.csv row 6 Z 51.295?
XXI_R6_exit.csv row 7 PHI -1.02?
XXI_R6_inlet.csv row 4 PHI 3.59?
XXI_R6_inlet.csv row 9 BETA 56.88?
XXI_R6_planesections.csv row 3 TTE/C 0.0116?
XXI_R6_planesections.csv row 7 CAMBER 17.60?
XXI_R6_planesections.csv row 7 TTE/C 0.0132?
XXI_R6_sldata.csv row 7 SOL 1.2912?
XXI_R7_exit.csv row 3 CZ 163.9?
XXI_R7_inlet.csv row 7 PHI 1.22?
XXI_R7_inlet.csv row 11 RADIUS 27.459?
XXI_R8_exit.csv row 2 PHI -2.72?
XXI_R8_exit.csv row 4 PHI 2.32?
XXI_R8_exit.csv row 9 PHI -0.05?
XXI_R8_sldata.csv row 5 INC -0.08?
XXI_R9_exit.csv row 1 PHI -2.52?
XXI_R9_exit.csv row 2 PHI -2.77?
XXI_R9_exit.csv row 4 PHI 2.53?
XXI_R9_exit.csv row 5 PHI 2.08?
XXI_R9_exit.csv row 6 PHI -1.59?
XXI_R9_inlet.csv row 3 PHI 2.90?
XXI_R9_inlet.csv row 9 PHI -0.10?
XXI_R9_inlet.csv row 10 BETA 59.13?
XXI_R9_planesections.csv row 2 BETA2* 37.39?
XXI_S10_exit.csv row 9 PHI 0.75?
XXI_S10_exit.csv row 11 PHI -1.36?
XXI_S10_inlet.csv row 8 PHI -0.80?
XXI_S1_exit.csv row 10 PHI 11.34?
XXI_S1_exit.csv row 11 PHI 13.95?
XXI_S1_exit.csv row 12 ALPHA 16.00?
XXI_S1_planesections.csv row 7 BETA2* 8.52?
XXI_S1_sldata.csv row 2 CUM EFF 0.7600?
XXI_S2_exit.csv row 1 PHI -3.77?
XXI_S2_exit.csv row 2 PHI -2.30?
XXI_S2_exit.csv row 3 PHI -1.20?
XXI_S2_exit.csv row 4 CZ 172.9?
XXI_S2_inlet.csv row 1 PHI -3.77?
XXI_S2_inlet.csv row 2 PHI -1.88?
XXI_S2_inlet.csv row 3 PHI -0.72?
XXI_S2_planesections.csv row 1 BETA1* 58.87?
XXI_S2_planesections.csv row 4 TM/C 0.0955?
XXI_S3_exit.csv row 2 PHI -3.25?
XXI_S3_exit.csv row 11 Z 33.756?
XXI_S3_inlet.csv row 1 ALPHA 59.81?
XXI_S3_inlet.csv row 11 PHI 7.86?
XXI_S4_inlet.csv row 1 PHI -4.84?
XXI_S4_inlet.csv row 6 RADIUS 29.463?
XXI_S4_planesections.csv row 3 BETA2* 15.45?
XXI_S5_exit.csv row 2 % IMM 8.5?
XXI_S5_inlet.csv row 2 PHI 3.52?
XXI_S5_planesections.csv row 1 BETA2* 20.90?
XXI_S5_planesections.csv row 5 BETA1* 46.58?
XXI_S5_sldata.csv row 1 DEV 13.81?
XXI_S5_sldata.csv row 6 DF 0.4883?
XXI_S5_sldata.csv row 8 DF 0.4871?
XXI_S6_exit.csv row 1 PHI 4.09?
XXI_S6_inlet.csv row 2 PHI -3.26?
XXI_S6_inlet.csv row 3 PHI 2.73?
XXI_S7_inlet.csv row 8 Z 58.290?
XXI_S8_exit.csv row 3 PHI -1.84?
XXI_S8_exit.csv row 11 PHI -0.33?
XXI_S8_inlet.csv row 9 PHI -0.93?
XXI_S8_planesections.csv row 5 SECT. HT. 28.956?
XXI_S8_planesections.csv row 8 BETA1* 46.56?
XXI_S9_exit.csv row 1 TT/TTI 2.6654?
XXI_S9_exit.csv row 1 PHI 2.52?
XXI_S9_exit.csv row 2 M-ABS 0.293?
XXI_S9_exit.csv row 2 PHI -2.11?
XXI_S9_exit.csv row 5 PHI -1.26?
XXI_S9_exit.csv row 6 % IMM 43.5?
XXI_S9_exit.csv row 7 PHI -1.18?
XXI_S9_exit.csv row 10 PHI 0.90?
XXI_S9_exit.csv row 11 PHI -0.48?
XXI_S9_exit.csv row 12 PHI -0.46?
XXI_S9_inlet.csv row 3 PHI -1.63?
XXI_S9_inlet.csv row 4 PHI -1.37?
XXI_S9_inlet.csv row 6 PHI -1.23?
XXI_S9_inlet.csv row 9 PHI -1.11?
XXI_S9_inlet.csv row 10 PHI -0.97?
XXI_S9_inlet.csv row 11 PHI -0.67?
XXI_S9_sldata.csv row 7 R-BAR 28.381?
```

Total: 174 cells.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

E3 sign rule applied uniformly in this pass (replaces the two worker rules described above): the sign printed on the SI page is recorded; a minus visible on the SI page is written without '?'; a minus printed only on the U.S. page is written as a minus with '?'; where neither page prints a minus although the radial PHI trend implies one, the printed unsigned value is kept with '?'. The list in 'Cells marked ?' above is superseded by this section.

Resolved 108, still '?' 66, print errors 3.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| CR165558_tableXXI_R10_exit.csv | 3 | PHI | `-2.52?` | `-2.52?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 4 | PHI | `-2.74?` | `-2.74?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 5 | PHI | `-2.78?` | `-2.78?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 6 | PHI | `-2.45?` | `-2.45?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 7 | PHI | `-1.95?` | `-1.95?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 8 | PHI | `-1.39?` | `-1.39?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 10 | PHI | `-0.40?` | `-0.40?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_exit.csv | 6 | U | `372.3?` | `372.3` | U.S. page 1221.5 ft/s x 0.3048 = 372.31; U = omega r: 378.8 x 28.899/29.406 = 372.27 | 600-dpi zoom: SI prints 3?2.3 with the middle digit lost; both checks give 372.3 |
| CR165558_tableXXI_R10_inlet.csv | 3 | PHI | `-2.52?` | `-2.52` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus; trend negative |
| CR165558_tableXXI_R10_inlet.csv | 4 | PHI | `2.83?` | `2.83?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-2.52, ?, -2.94) |
| CR165558_tableXXI_R10_inlet.csv | 5 | PHI | `-2.94?` | `-2.94?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_inlet.csv | 6 | PHI | `-2.63?` | `-2.63?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_inlet.csv | 7 | PHI | `-2.12?` | `-2.12?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_inlet.csv | 8 | PHI | `-1.55?` | `-1.55?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_inlet.csv | 9 | PHI | `-0.99?` | `-0.99` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus |
| CR165558_tableXXI_R10_inlet.csv | 10 | Z | `73.479?` | `73.479?` | U.S. page 28.929 in x 2.54 = 73.480 (73.478-73.481 over rounding); trend 73.490, -, 73.466 | 600-dpi zoom: SI last digit lost (73.47?); 73.478-73.480 all possible, still uncertain, kept |
| CR165558_tableXXI_R10_inlet.csv | 10 | PHI | `-0.47?` | `-0.47?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_inlet.csv | 11 | PHI | `-0.01?` | `-0.01?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_planesections.csv | 3 | BETA1* | `66.48?` | `66.48` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = BETA1* - BETA2* = 66.48 - 37.32 = 29.16 (printed 29.17) |
| CR165558_tableXXI_R10_sldata.csv | 9 | LOSS | `0.0553?` | `0.0553` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R10_sldata.csv | 12 | INC | `-0.62?` | `-0.62?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_sldata.csv | 13 | INC | `-1.35?` | `-1.35?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R10_sldata.csv | 14 | INC | `-2.00?` | `-2.00?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R1_exit.csv | 13 | RADIUS | `21.232?` | `21.232` | U.S. page 8.359 in x 2.54 = 21.232 (21.231-21.233); R-BAR = (19.306 + 21.232)/2 = 20.269 = printed R-BAR | 600-dpi zoom: SI 21.2 plus two broken glyphs with the shapes of 3 and 2; checks agree |
| CR165558_tableXXI_R1_exit.csv | 14 | RADIUS | `20.343?` | `20.343` | U.S. page 8.009 in x 2.54 = 20.343 (20.342-20.344); R-BAR = (17.795 + 20.343)/2 = 19.069 = printed R-BAR | 600-dpi zoom: SI last glyph a broken 3 (flat top, right side); 20.347 excluded by the U.S. page; checks agree |
| CR165558_tableXXI_R1_inlet.csv | 13 | M-ABS | `0.484?` | `0.484` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R1_sldata.csv | 4 | INC | `3.20?` | `3.20` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R2_exit.csv | 11 | M-REL | `0.621?` | `0.621` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R2_exit.csv | 14 | M-ABS | `0.785?` | `0.785` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R2_planesections.csv | 12 | CHORD | `6.7282?` | `6.7282` | U.S. page 2.6489 in x 2.54 = 6.7282 (6.7281-6.7283) | 600-dpi zoom: SI 6.7?82 with the third glyph partly lost (2-like); U.S. conversion agrees |
| CR165558_tableXXI_R2_sldata.csv | 9 | R-BAR | `27.917?` | `27.917` | R-BAR = (27.757 + 28.076)/2 = 27.9165; U.S. page 10.991 in x 2.54 = 27.917 | 600-dpi zoom: SI 2?.?17 with broken 7 and 9; checks agree |
| CR165558_tableXXI_S1_exit.csv | 12 | PHI | `11.34?` | `11.34` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI prints .1.34 (first 1 broken) |
| CR165558_tableXXI_S1_exit.csv | 13 | PHI | `13.95?` | `13.95` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI prints 1?.95 |
| CR165558_tableXXI_S1_exit.csv | 14 | ALPHA | `16.00?` | `16.00` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI prints 16.0 with the last 0 broken |
| CR165558_tableXXI_S1_planesections.csv | 9 | BETA2* | `8.52?` | `8.52` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = BETA1* - BETA2* = 44.59 - 8.52 = 36.07 (printed 36.07) |
| CR165558_tableXXI_S1_sldata.csv | 4 | CUM EFF | `0.7600?` | `0.7600` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI third glyph is a 6 with the upper-left stroke lost (closed lower loop), reads like 3 at low zoom |
| CR165558_tableXXI_R3_exit.csv | 6 | PHI | `-2.62?` | `-2.62?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R3_exit.csv | 7 | PHI | `-0.82?` | `-0.82?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R3_exit.csv | 10 | U | `361.7?` | `361.7` | U.S. page 1186.8 ft/s x 0.3048 = 361.74; U = omega r trend 370.5, -, 352.9 | 600-dpi zoom: SI 3?1.7 with the second digit broken (6-like); checks agree |
| CR165558_tableXXI_R3_inlet.csv | 4 | PHI | `-3.58?` | `-3.58?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R3_inlet.csv | 5 | PHI | `-2.25?` | `-2.25?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R3_inlet.csv | 6 | PHI | `-0.61?` | `-0.61?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R3_inlet.csv | 5 | PT/PTI | `2.6204?` | `2.6204` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; trend 2.6081, -, 2.6337 |
| CR165558_tableXXI_R3_inlet.csv | 12 | TT/TTI | `1.3756?` | `1.3756` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; R2 exit TT/TTI SL10 = 1.3756 (no work between R2 exit and R3 inlet except S2: S2 prints 1.3756) |
| CR165558_tableXXI_R3_inlet.csv | 13 | TT/TTI | `1.3975?` | `1.3975` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; R2 exit TT/TTI SL11 = 1.3975 |
| CR165558_tableXXI_R3_planesections.csv | 5 | CAMBER | `10.92?` | `10.92` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = BETA1* - BETA2* = 61.00 - 50.08 = 10.92 |
| CR165558_tableXXI_R3_sldata.csv | 3 | INC | `1.00?` | `1.00` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_S2_exit.csv | 3 | PHI | `-3.77?` | `-3.77?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S2_exit.csv | 4 | PHI | `-2.30?` | `-2.30?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S2_exit.csv | 5 | PHI | `-1.20?` | `-1.20?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S2_exit.csv | 6 | CZ | `172.9?` | `172.9` | U.S. page 567.2 ft/s x 0.3048 = 172.88 (172.87-172.90) | 600-dpi zoom: SI 172. with the tenths glyph broken (9-like); U.S. conversion agrees |
| CR165558_tableXXI_S2_inlet.csv | 3 | PHI | `-3.77?` | `-3.77?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S2_inlet.csv | 4 | PHI | `-1.88?` | `-1.88?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S2_inlet.csv | 5 | PHI | `-0.72?` | `-0.72?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S2_planesections.csv | 3 | BETA1* | `58.87?` | `58.87` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = 58.87 - 19.45 = 39.42 (printed 39.41) |
| CR165558_tableXXI_S2_planesections.csv | 6 | TM/C | `0.0955?` | `0.0955` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R4_exit.csv | 3 | PHI | `4.84?` | `4.84?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (?, -5.06 at SL2; S4 inlet SL1 prints -4.84 on the U.S. page) |
| CR165558_tableXXI_R4_exit.csv | 13 | RADIUS | `26.799?` | `26.799` | U.S. page 10.551 in x 2.54 = 26.7995 (26.798-26.801); R-BAR = (26.513 + 26.799)/2 = 26.656 = printed | 600-dpi zoom: SI 26 ?99 with the 7 broken and the decimal point lost; the visible 99 excludes 26.800; checks agree |
| CR165558_tableXXI_R4_inlet.csv | 4 | CZ | `173.2?` | `173.2` | U.S. page 568.3 ft/s x 0.3048 = 173.22 (173.20-173.23) | 600-dpi zoom: SI 173 with the tenths glyph broken (2-like); U.S. conversion agrees |
| CR165558_tableXXI_R4_sldata.csv | 7 | DF | `0.4425?` | `0.4425` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R5_exit.csv | 13 | M-ABS | `0.644?` | `0.644` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R5_exit.csv | 14 | M-ABS | `0.650?` | `0.650` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R5_inlet.csv | 3 | PHI | `4.84?` | `4.84?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (?, -5.00 at SL2) |
| CR165558_tableXXI_R5_inlet.csv | 7 | PHI | `2.55?` | `-2.55?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?'; trend -3.51, -, -1.63; the earlier transcription had dropped the U.S.-page minus, now written per the rule |
| CR165558_tableXXI_R5_inlet.csv | 12 | M-ABS | `0.484?` | `0.484` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R5_inlet.csv | 13 | CZ | `194.2?` | `194.2` | U.S. page 637.3 ft/s x 0.3048 = 194.25 (194.23-194.26, i.e. 194.2 or 194.3) | 600-dpi zoom: SI ?94 2 with the tenths 2 legible; with the U.S. page this fixes 194.2 |
| CR165558_tableXXI_R5_inlet.csv | 14 | CZ | `189.1?` | `189.1?` | U.S. page 620.4 ft/s x 0.3048 = 189.10 (189.09-189.11) | 600-dpi zoom: SI digits illegible (18 and fragments); value is a U.S.-page conversion, kept with '?' |
| CR165558_tableXXI_R5_sldata.csv | 9 | LOSS | `0.0433?` | `0.0433` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_S4_inlet.csv | 3 | PHI | `-4.84?` | `-4.84?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?'; SI shows only a fragment where the 4 should be; no separate minus identifiable |
| CR165558_tableXXI_S4_inlet.csv | 8 | RADIUS | `29.463?` | `29.463` | U.S. page 11.600 in x 2.54 = 29.464 (29.463-29.465); R-BAR = (29.463 + 29.444)/2 = 29.454 = printed | 600-dpi zoom: SI 29 4?3 with the last digit 3 legible; checks agree |
| CR165558_tableXXI_S4_planesections.csv | 5 | BETA2* | `15.45?` | `15.45` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = 48.25 - 15.45 = 32.80 (printed 32.80) |
| CR165558_tableXXI_R6_exit.csv | 3 | PT/PTI | `9.8070?` | `9.8070` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R6_exit.csv | 7 | TT/TTI | `2.0194?` | `2.0194` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R6_exit.csv | 8 | Z | `51.295?` | `51.295` | U.S. page 20.195 in x 2.54 = 51.295 (51.294-51.296); trend 51.267, -, 51.327 | 600-dpi zoom: SI 51.2?5 with the middle glyph a broken 9 (3-like); checks fix 9 |
| CR165558_tableXXI_R6_exit.csv | 9 | PHI | `-1.02?` | `-1.02?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R6_inlet.csv | 6 | PHI | `3.59?` | `3.59?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-4.36, ?, -2.76) |
| CR165558_tableXXI_R6_inlet.csv | 11 | BETA | `56.88?` | `56.88` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R6_planesections.csv | 5 | TTE/C | `0.0116?` | `0.0116` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R6_planesections.csv | 9 | CAMBER | `17.60?` | `17.60` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = 58.30 - 40.71 = 17.59 |
| CR165558_tableXXI_R6_planesections.csv | 9 | TTE/C | `0.0132?` | `0.0132` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_R6_sldata.csv | 9 | SOL | `1.2912?` | `1.2912` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_S5_exit.csv | 4 | % IMM | `8.5?` | `8.5` | U.S. page prints 8.5; SL DATA % IMM is the mean of inlet and exit (R10: 4.5/5.4 -> 4.9): (9.2 + 8.5)/2 = 8.85, printed 8.8; 6.5 would give 7.85 | 600-dpi zoom: SI glyph is a blotted 8 that reads like 6; both checks give 8.5 |
| CR165558_tableXXI_S5_inlet.csv | 4 | PHI | `3.52?` | `-3.52` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus; trend -4.84, -, -3.04 |
| CR165558_tableXXI_S5_planesections.csv | 3 | BETA2* | `20.90?` | `20.90` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = 61.08 - 20.90 = 40.18 (printed 40.18) |
| CR165558_tableXXI_S5_planesections.csv | 7 | BETA1* | `46.58?` | `46.58` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = 46.58 - 11.35 = 35.23 (printed 35.23) |
| CR165558_tableXXI_S5_sldata.csv | 3 | DEV | `13.81?` | `13.81` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_S5_sldata.csv | 8 | DF | `0.4883?` | `0.4883` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_S5_sldata.csv | 10 | DF | `0.4871?` | `0.4871` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved |
| CR165558_tableXXI_S6_exit.csv | 3 | PHI | `4.09?` | `4.09?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (?, -3.28 on the U.S. page at SL2; S6 inlet SL1 prints -4.09) |
| CR165558_tableXXI_S6_inlet.csv | 4 | PHI | `-3.26?` | `-3.26` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus; trend -4.09, -, -2.73(?) |
| CR165558_tableXXI_S6_inlet.csv | 5 | PHI | `2.73?` | `2.73?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-3.26, ?, -2.25) |
| CR165558_tableXXI_R7_exit.csv | 5 | CZ | `163.9?` | `163.9` | U.S. page 537.6 ft/s x 0.3048 = 163.86 (163.84-163.87) | 600-dpi zoom: SI 16?.9 with the 3 broken; U.S. conversion agrees |
| CR165558_tableXXI_R7_inlet.csv | 9 | PHI | `1.22?` | `1.22?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-1.94, ?, -0.51) |
| CR165558_tableXXI_R7_inlet.csv | 13 | RADIUS | `27.459?` | `27.459` | R-BAR = (27.459 + 27.503)/2 = 27.481 = printed (27.453 would give 27.478); U.S. page 10.810 in x 2.54 = 27.457 (27.456-27.459) | 600-dpi zoom: SI last glyph a broken 9 that reads like 3; checks fix 9 |
| CR165558_tableXXI_R8_exit.csv | 4 | PHI | `-2.72?` | `-2.72` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus; trend -2.52, -, -2.67 |
| CR165558_tableXXI_R8_exit.csv | 6 | PHI | `2.32?` | `2.32?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-2.67, ?, -1.85) |
| CR165558_tableXXI_R8_exit.csv | 11 | PHI | `-0.05?` | `-0.05` | SI/U.S. page pair; sign rule | 600-dpi zoom: minus visible on both pages; printed sign recorded without '?' |
| CR165558_tableXXI_R8_sldata.csv | 7 | INC | `-0.08?` | `-0.08` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus |
| CR165558_tableXXI_S7_inlet.csv | 10 | Z | `58.290?` | `58.290` | U.S. page 22.949 in x 2.54 = 58.290 (58.289-58.292); trend 58.284, -, 58.302 | 600-dpi zoom: SI 58.2?0 with a broken 9; checks agree |
| CR165558_tableXXI_S8_exit.csv | 5 | PHI | `-1.84?` | `-1.84` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus; trend -2.21, -, -1.57 |
| CR165558_tableXXI_S8_exit.csv | 13 | PHI | `-0.33?` | `-0.33?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S8_inlet.csv | 11 | PHI | `-0.93?` | `-0.93?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S8_planesections.csv | 7 | SECT. HT. | `28.956?` | `28.956` | SECT. HT. = R-BAR = (28.987 + 28.946)/2 = 28.966 (printed R-BAR 28.966); U.S. page 11.404 in x 2.54 = 28.966 | PRINT ERROR: 600-dpi zoom shows 28.956 clearly on the SI page; kept as printed without '?', both checks give 28.966 |
| CR165558_tableXXI_S8_planesections.csv | 10 | BETA1* | `46.56?` | `46.56` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; CAMBER = 46.56 - 4.44 = 42.12 (printed 42.11) |
| CR165558_tableXXI_S10_exit.csv | 11 | PHI | `0.75?` | `0.75?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (0.41, -0.22, ?, -1.15, -1.36) |
| CR165558_tableXXI_S10_exit.csv | 13 | PHI | `-1.36?` | `-1.36?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S10_inlet.csv | 10 | PHI | `-0.80?` | `-0.80` | U.S. page prints -0.90 for the same cell; trend -0.68, -, -0.87 admits both | PRINT DISAGREEMENT: 600-dpi zoom shows -0.80 clearly on the SI page (minus visible) and -0.90 clearly on the U.S. page; SI value kept as printed without '?'; which page is wrong is not decidable |
| CR165558_tableXXI_R9_exit.csv | 3 | PHI | `-2.52?` | `-2.52?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R9_exit.csv | 4 | PHI | `-2.77?` | `-2.77?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R9_exit.csv | 6 | PHI | `2.53?` | `2.53?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-2.82, ?, ?, -1.59) |
| CR165558_tableXXI_R9_exit.csv | 7 | PHI | `2.08?` | `2.08?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-2.82, ?, ?, -1.59) |
| CR165558_tableXXI_R9_exit.csv | 8 | PHI | `-1.59?` | `-1.59?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R9_inlet.csv | 5 | PHI | `2.90?` | `2.90?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-2.80, ?, -2.63) |
| CR165558_tableXXI_R9_inlet.csv | 11 | PHI | `-0.10?` | `-0.10?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_R9_inlet.csv | 12 | BETA | `59.13?` | `59.13` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI prints 59.?3 |
| CR165558_tableXXI_R9_planesections.csv | 4 | BETA2* | `37.39?` | `37.89` | CAMBER = BETA1* - BETA2* = 64.30 - 37.89 = 26.41 (printed 26.41; 37.39 would give 26.91); U.S. page prints 37.89; Table XXII R9 (= Table XXI + 2.00) prints 39.89 | 600-dpi zoom: SI third glyph is an 8 with the left strokes lost (reads like 3); reading corrected to 37.89 by three checks |
| CR165558_tableXXI_S9_inlet.csv | 5 | PHI | `-1.63?` | `-1.63` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus |
| CR165558_tableXXI_S9_inlet.csv | 6 | PHI | `-1.37?` | `-1.37?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_inlet.csv | 8 | PHI | `-1.23?` | `-1.23?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_inlet.csv | 11 | PHI | `-1.11?` | `-1.11?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_inlet.csv | 12 | PHI | `-0.97?` | `-0.97?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_inlet.csv | 13 | PHI | `-0.67?` | `-0.67?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_exit.csv | 3 | PHI | `2.52?` | `2.52?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (S9 inlet SL1 -2.52; exit SL2 -2.11) |
| CR165558_tableXXI_S9_exit.csv | 4 | PHI | `-2.11?` | `-2.11` | SI/U.S. page pair; sign rule | 600-dpi zoom: a minus (small tick before the digits) is visible on the SI page; printed sign recorded without '?'; U.S. page shows no minus |
| CR165558_tableXXI_S9_exit.csv | 7 | PHI | `-1.26?` | `-1.26?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_exit.csv | 9 | PHI | `-1.18?` | `-1.18?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_exit.csv | 13 | PHI | `-0.48?` | `-0.48?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_exit.csv | 14 | PHI | `-0.46?` | `-0.46?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S9_exit.csv | 12 | PHI | `0.90?` | `0.90?` | SI/U.S. page pair; radial PHI trend | 600-dpi zoom: no minus visible on either page although the radial trend of the neighbouring streamlines implies a negative value; printed (unsigned) value kept with '?'; (-1.07, ?, -0.48) |
| CR165558_tableXXI_S9_exit.csv | 3 | TT/TTI | `2.6654?` | `2.6654` | U.S. page 2.6654; stator: exit TT/TTI = inlet TT/TTI SL1 = 2.6654 | 600-dpi zoom: SI 2.6654 legible; checks agree |
| CR165558_tableXXI_S9_exit.csv | 4 | M-ABS | `0.293?` | `0.299` | U.S. page prints 0.299 (Mach number, unit-independent); trend 0.294, -, 0.305 | 600-dpi zoom: SI last glyph is a broken 9 that reads like 3; reading corrected to 0.299 from the U.S. page |
| CR165558_tableXXI_S9_exit.csv | 8 | % IMM | `43.5?` | `43.5` | U.S. page 43.5; SL DATA % IMM = mean of inlet and exit = (44.3 + 43.5)/2 = 43.9 = printed | 600-dpi zoom: SI 4?.5 with the 3 broken; checks agree |
| CR165558_tableXXI_S9_sldata.csv | 9 | R-BAR | `28.381?` | `28.381` | R-BAR = (28.401 + 28.361)/2 = 28.381; U.S. page 11.174 in x 2.54 = 28.382 (28.381-28.383) | 600-dpi zoom: SI 28.3?1 with a broken 8; checks agree |
| CR165558_tableXXI_S3_exit.csv | 4 | PHI | `-3.25?` | `-3.25?` | SI/U.S. page pair (angles unit-independent); sign rule | 600-dpi zoom: no minus visible on the SI page, minus printed on the U.S. page; by the uniform E3 sign rule the value keeps the minus and the '?' |
| CR165558_tableXXI_S3_exit.csv | 13 | Z | `33.756?` | `33.756?` | U.S. page 13.290 in x 2.54 = 33.757 (33.755-33.758); trend 33.792, -, 33.702 | 600-dpi zoom (skewed scan): SI 33.75 plus a broken last glyph; 33.755-33.758 all possible, still uncertain, kept |
| CR165558_tableXXI_S3_inlet.csv | 3 | ALPHA | `59.81?` | `59.81` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI prints 59 ?1 (8 broken) |
| CR165558_tableXXI_S3_inlet.csv | 13 | PHI | `7.86?` | `7.86` | U.S.-unit facing page (unit-independent column) | 600-dpi zoom: SI glyph damaged, U.S. page prints the value clearly; resolved; SI prints 7 ?6 (8 broken, 3-like); trend 6.09, -, 8.88 |
| CR165558_tableXXII_IGV.csv | 3 | (CHORD) | `2.466?` | `2.466` | CHORD/2.54 = 6.2627/2.54 = 2.4656 | 600-dpi zoom: (?.466) with the leading 2 broken; conversion fixes 2 |
| CR165558_tableXXII_R1.csv | 9 | BETA2* | `43.82?` | `13.82` | CAMBER = BETA1* - BETA2* gives 55.88 - 12.06 = 43.82; Table XXI 41.77 (+2.05 restagger) | PRINT ERROR: 600-dpi zoom shows 13.82 clearly (a clean 1, not a broken 4); printed value kept without '?', the relation gives 43.82 |
| CR165558_tableXXII_R10.csv | 13 | STAGGER | `48.63?` | `48.63` | Table XXII R10 = Table XXI + 2.00: 46.63 + 2.00 = 48.63 | 600-dpi zoom: 48 ?3 with the tenths digit lost; relation fixes 6 |
| CR165558_tableXXII_R3.csv | 11 | BETA1* | `53.07?` | `53.07` | CAMBER + BETA2* = 22.90 + 30.16 = 53.06 (rounding) | 600-dpi zoom: 5?.07 with a broken 3; relation agrees |
| CR165558_tableXXII_R3.csv | 13 | TTE/C | `0.0116?` | `0.0116` | radial trend 0.0095, 0.0102, -, 0.0128; Table XXI same section 0.0117 | 600-dpi zoom: third decimal digit is a thin broken vertical stroke (1, not the wide 0); reading 0.0116 |
| CR165558_tableXXII_R5.csv | 8 | TTE/C | `0.0128?` | `0.0128` | Table XXI R5 same section prints 0.0128 and every other column of this row is identical to Table XXI; trend 0.0124, -, 0.0132 | 600-dpi zoom: last glyph is an 8 with its left strokes dropped (reads like 3); checks give 0.0128 |
| CR165558_tableXXII_R5.csv | 14 | BETA1* | `52.98?` | `52.98` | CAMBER + BETA2* = 36.15 + 16.84 = 52.99 (rounding); Table XXI 52.98 | 600-dpi zoom: 5?.98 with a broken 2; checks agree |
| CR165558_tableXXII_R6.csv | 6 | BETA1* | `60.71?` | `60.71` | CAMBER + BETA2* = 17.82 + 42.90 = 60.72 (rounding); Table XXI same section 60.71 (row identical to Table XXI) | 600-dpi zoom: 60.7? with the last 1 broken; checks agree |
| CR165558_tableXXII_R7.csv | 6 | CAMBER | `19.53?` | `19.53` | CAMBER = BETA1* - BETA2* = 60.06 - 40.53 = 19.53; Table XXI same section 19.53 (row identical) | 600-dpi zoom: second glyph reads like 3; in this font a 9 that loses the left side of its loop keeps the 3-like bowl-tail, so the glyph is consistent with a damaged 9; relation fixes 19.53 |
| CR165558_tableXXII_R8.csv | 13 | TTE/C | `0.0147?` | `0.0147` | Table XXII R8 = Table XXI except stagger/metal angles (+2.00); Table XXI prints 0.0147; trend 0.0143, -, 0.0149 | 600-dpi zoom: 0.014 plus a broken last glyph (7-like); checks agree |
| CR165558_tableXXII_R9.csv | 10 | (SECT. HT.) | `11.107?` | `11.107` | SECT. HT./2.54 = 28.212/2.54 = 11.1071 | 600-dpi zoom: (1?.107) with the second 1 broken; conversion agrees |
| CR165558_tableXXII_R9.csv | 11 | SECT. HT. | `27.985?` | `27.985` | (SECT. HT.) 11.018 x 2.54 = 27.986; Table XXI R9 SECT. HT. 27.985 | 600-dpi zoom: ?7.985 with the leading 2 broken; checks agree |
| CR165558_tableXXII_S1.csv | 13 | BETA2* | `-2.89?` | `-2.89?` | CAMBER relation BETA1* - CAMBER = 41.67 - 44.55 = -2.88; neighbours -1.98, -2.93 print minus | 600-dpi zoom: 2.89 printed with no visible minus (no U.S. page exists for Table XXII); relation requires a minus; sign uncertain in the print, kept as -2.89? |
| CR165558_tableXXII_S10.csv | 6 | BETA1* | `49.58?` | `49.58` | CAMBER + BETA2* = 55.08 - 5.50 = 49.58; Table XXI S10 same (unchanged row) | 600-dpi zoom: 4?.58 with a broken 9; checks agree |
| CR165558_tableXXII_S10.csv | 14 | (SECT. HT.) | `10.773?` | `10.773` | SECT. HT./2.54 = 27.364/2.54 = 10.7732 | 600-dpi zoom: (?0.773) with the leading 1 broken; conversion agrees |
| CR165558_tableXXII_S10.csv | 14 | BETA1* | `62.58?` | `62.58` | CAMBER + BETA2* = 71.28 - 8.70 = 62.58; Table XXI S10 62.58 | 600-dpi zoom: 6? 58 with a broken 2; checks agree |
| CR165558_tableXXII_S3.csv | 14 | CHORD | `2.8194?` | `2.8184` | Table XXI S3 same section prints 2.8184 and every other cell of this Table XXII row equals Table XXI; XXI hub chords 2.8184 on rows 10-12; (1.110) in fits both | 600-dpi zoom: third decimal glyph has a closed upper loop and an open lower-left (9-like), the dropout pattern of an 8 in this scan (row 11 prints a full 8); reading changed to 2.8184 by the Table XXI check |
| CR165558_tableXXII_S4.csv | 10 | (SECT. HT.) | `11.217?` | `11.217` | SECT. HT./2.54 = 28.491/2.54 = 11.2169 | 600-dpi zoom: (11.?17) with a broken 2; conversion agrees |
| CR165558_tableXXII_S4.csv | 11 | CHORD | `2.4891?` | `2.4881` | Table XXI S4 same section prints 2.4881 and every other cell of this row equals Table XXI; (0.980) in fits both | 600-dpi zoom: third decimal glyph is 9-like with an open lower-left (8 dropout pattern; row 10 prints a full 8); reading changed to 2.4881 by the Table XXI check |
| CR165558_tableXXII_S5.csv | 9 | SECT. HT. | `28.883?` | `28.883` | (11.371) x 2.54 = 28.882; Table XXI S5 SECT. HT. 28.883 | 600-dpi zoom: ?8.883 with the leading 2 lost; checks agree |
| CR165558_tableXXII_S5.csv | 10 | SECT. HT. | `28.487?` | `28.487` | (11.215) x 2.54 = 28.486; Table XXI 28.487 | 600-dpi zoom: 28.4?7 with a broken 8; checks agree |
| CR165558_tableXXII_S5.csv | 10 | CAMBER | `36.22?` | `36.22` | BETA1* - BETA2* = 46.91 - 10.68 = 36.23 (rounding); Table XXI 36.22 | 600-dpi zoom: 36.22 with the last 2 thin but complete; checks agree |
| CR165558_tableXXII_S6.csv | 5 | SECT. HT. | `30.071?` | `30.071` | (11.839) x 2.54 = 30.071; Table XXI 30.071 | 600-dpi zoom: 30.07? with a broken 1; checks agree |
| CR165558_tableXXII_S6.csv | 6 | SECT. HT. | `29.732?` | `29.732` | (11.706) x 2.54 = 29.733; Table XXI 29.732 | 600-dpi zoom: 29.7?2 with a broken 3; checks agree |
| CR165558_tableXXII_S7.csv | 3 | (SECT. HT.) | `11.871?` | `11.871` | SECT. HT./2.54 = 30.152/2.54 = 11.8709 | 600-dpi zoom: (?1.871) with the leading 1 broken; conversion agrees |
| CR165558_tableXXII_S8.csv | 4 | STAGGER | `33.99?` | `33.99` | circular-arc relation STAGGER = (BETA1* + BETA2*)/2 = (59.03 + 8.94)/2 = 33.985 (holds on S8 rows TIP, 2, 5) | 600-dpi zoom: 33 99 with the second 9 smudged; relation agrees |
| CR165558_tableXXII_S8.csv | 7 | BETA1* | `49.17?` | `49.17` | CAMBER + BETA2* = 46.12 + 3.05 = 49.17 | 600-dpi zoom: 4? 17 with a broken 9; relation fixes 49.17 |
| CR165558_tableXXII_S8.csv | 9 | STAGGER | `24.93?` | `24.93?` | no exact relation on S8 rows 6-9 (circular-arc mean does not hold there: row 6 25.315 vs 25.34, row 9 25.38 vs 24.53); trend 25.34, -, 24.54 | 600-dpi zoom: 24.?? with both decimal glyphs damaged (9- and 3/8-like); still uncertain, kept |
| CR165558_tableXXII_S8.csv | 10 | STAGGER | `24.54?` | `24.54` | no exact relation (see row 7); trend 24.93, -, 24.53 | 600-dpi zoom: 24.5 plus a damaged last glyph that keeps the open-top 4 shape of this font; reading 24.54 |
| CR165558_tableXXII_S8.csv | 13 | STAGGER | `27.61?` | `27.61` | no exact relation; trend 25.28, -, 29.71 fixes 27.x | 600-dpi zoom: 2?.6? with a broken 7 (top bar and stem visible) and a broken 1 (stem with gap); reading 27.61 |
| CR165558_tableXXII_S8.csv | 14 | TTE/C | `0.0141?` | `0.0141` | no exact relation; trend 0.0123, 0.0134, - (rising to the hub) | 600-dpi zoom: 0.014 plus a thin broken vertical stroke (1); reading 0.0141 |
| CR165558_tableXXII_S9.csv | 3 | (CHORD) | `0.912?` | `0.912` | CHORD/2.54 = 2.3158/2.54 = 0.9117 | 600-dpi zoom: (0.9?2) with a broken 1; conversion agrees |
| CR165558_tableXXII_S9.csv | 6 | BETA1* | `53.15?` | `53.15` | CAMBER + BETA2* = 49.59 + 3.56 = 53.15 | 600-dpi zoom: 5?.15 with a broken 3; relation agrees |
| CR165558_tableXXII_S9.csv | 7 | CHORD | `2.1585?` | `2.1585` | (CHORD) 0.850 x 2.54 = 2.159 (2.1577-2.1603); trend 2.1844, -, 2.1425 | 600-dpi zoom: 2.?585 with a broken 1; checks agree |
| CR165558_tableXXII_S9.csv | 7 | (CHORD) | `0.850?` | `0.850` | CHORD/2.54 = 2.1585/2.54 = 0.8498 | 600-dpi zoom: (0.?50) with a broken 8; conversion agrees |
| CR165558_tableXXII_S9.csv | 7 | TTE/C | `0.0121?` | `0.0121` | no exact relation; trend 0.0123, -, 0.0120 | 600-dpi zoom: 0.012 plus a thin broken vertical stroke (1); reading 0.0121 |
| CR165558_tableXXII_S9.csv | 12 | BETA1* | `53.65?` | `53.65` | CAMBER + BETA2* = 52.20 + 1.45 = 53.65 | 600-dpi zoom: 5?.65 with a broken 3; relation agrees |

Print errors / print disagreements found in this pass:

- CR165558_tableXXI_S8_planesections.csv row 7 SECT. HT.: printed `28.956`; SECT. HT. = R-BAR = (28.987 + 28.946)/2 = 28.966 (printed R-BAR 28.966); U.S. page 11.404 in x 2.54 = 28.966.
- CR165558_tableXXI_S10_inlet.csv row 10 PHI: printed `-0.80`; U.S. page prints -0.90 for the same cell; trend -0.68, -, -0.87 admits both.
- CR165558_tableXXII_R1.csv row 9 BETA2*: printed `13.82`; CAMBER = BETA1* - BETA2* gives 55.88 - 12.06 = 43.82; Table XXI 41.77 (+2.05 restagger).
