# P&W core compressor exit stage study (3S1 / 3S2): transcription notes

Sources: NASA CR-159714 (design, Burdsall, Canal, Lyons, 1979) and NASA CR-159812 (test, Behlke,
Burdsall, Canal, Kerr, 1979). All PDF page numbers are 1-based PDF indices.

Two low-speed three-stage rigs (IGV + 3 stages), same flowpath, same design flow and speed;
3S1 aspect ratio 0.81, 3S2 aspect ratio 1.22 (3S2 axial spacing scaled by the chord change).

## What is here

| Content | File(s) |
|---|---|
| Design parameters, per-row aspect ratios | `CR159714_tableI_design_parameters.csv` |
| Airfoil geometry on conical surfaces, every row of both rigs (IGV, R1, S1, R2, S2, R3, S3), 11 streamlines, SI and English blocks | `CR159714_appD_<rig>_<row>.csv` (14 files) |
| Airfoil aerodynamic summary, every row of both rigs, 11 streamlines | `CR159714_appC_<rig>_<row>_{1,2,3,overall}.csv` (1 = SI velocity block, 2 = angles/Mach/loss/efficiency block, 3 = English velocity block with PCT SPAN, overall = bottom line) |
| Measured overall performance and running tip clearance | `CR159812_tableIII_overall_performance.csv` |
| Instrumentation planes (stations 0-9), rake immersions, circumferential positions | `CR159812_tableII_performance_instrumentation.csv` |
| Scalars (speeds, flowpath, clearances, profile type, conventions, stations) | `scalars.json` |

## Appendix D (airfoil geometry on conical surfaces) conventions

- Each page has an SI block and an English block side by side, each in two sub-blocks
  (DIA LE, DIA TE, BETA 1*, BETA 2*, CHORD / O/TAU, TAU/B, T/B, LER, TER). The CSV puts both
  sub-blocks on one line per streamline; the first 10 data columns are SI, the next 10 English.
  The duplicated headings are told apart by the units row. The streamline number column is
  not printed (rows are in printed order, hub first: DIA LE 55.7530 cm = hub, 60.9600 cm = tip).
- Symbols (PDF p. 68): DIA LE/TE = D_LE/D_TE (diameter of the section's cone at LE/TE),
  BETA 1*/2* = metal angles beta*_LE / beta*_TE, CHORD = b, O/TAU = o/s (throat/pitch),
  TAU/B = s/b (pitch/chord = 1/solidity), T/B = t/b, LER/TER = edge radii.
- O/TAU is blank for both IGVs (printed blank).
- Metal angle beta*: "angle between tangent to mean camber line and meridional direction"
  (Appendix A, PDF p. 47). Air angles are defined there as "COT-1 (Vm/Vtheta)" (literal
  reading: measured from the tangential direction) but the tabulated values (rotor
  beta1* about 60-73 deg, stator exit about 20 deg) are consistent with angles from the
  meridional direction, like the metal angle. Interpretation is left to the code step.
- The rotor English-block diameters and angles have 4 decimals; IGV English diameters and
  angles have 3 decimals (as printed).

## Second read of Appendix D (this session)

All 14 CSVs were re-read cell by cell from 300 dpi renders (rotated). Corrections:
- `3S2_R1`, streamline 5, SI TAU/B: was 0.9055, printed 0.9065 (and English 0.9065). Fixed.
- `3S2_S3`, streamline 5, English BETA 1*: printed glyph "58.2?47" (3 or 8), now `58.2847?`
  (1.0173 rad = 58.29 deg).
- `3S1_R3`, streamline 4, English TAU/B printed clearly 0.8934: `?` removed (SI cell keeps `?`).
- A first header row ("SI UNITS ... ENGLISH UNITS") was removed so that row 1 = headings,
  row 2 = units, per the guide.

Cells still marked `?` (glyph damaged or partly missing; value given is the reading
consistent with the other unit block):
- 3S1 IGV: SI DIA TE sl 7 `58.928?` (last digit missing in print), SI DIA TE sl 8 `59.4411?`,
  SI T/B sl 5 `0.0832?` (glyph looks like 0.0332; English block 0.0832), English TAU/B sl 2
  `0.8778?` (SI block 0.8773).
- 3S1 S2: English BETA 2* sl 5 `22.4206?`.
- 3S1 R3: SI DIA TE sl 2 `56.3814?`, SI DIA LE sl 4 `57.4292?`, SI TAU/B sl 4 `0.8934?`.
- 3S1 S3: SI DIA TE sl 5 `57.9148?`, English BETA 2* sl 2 `20.9002?`.
- 3S2 R2: English BETA 1* sl 8 `61.5870?`.
- 3S2 S3: English BETA 1* sl 2 `64.8078?`, sl 5 `58.2847?`, sl 10 `62.6659?`, sl 11 `67.2183?`.

Printed inconsistencies (copied as printed):
- 3S2 IGV sl 9: SI DIA TE printed 59.9640 cm, larger than DIA LE 59.9542 and not equal to the
  English 23.600 in (= 59.944 cm). Probably a print slip for 59.9440.
- 3S2 IGV sl 10: SI LER 0.0258 cm while English LER is 0.009 in; 3S1 IGV has 0.0254 / 0.010 and
  0.0279 / 0.011 at sl 10/11, 3S2 IGV has 0.0228 at sl 11.
- 3S1 IGV sl 2: TAU/B SI 0.8773 vs English 0.8778.
- Radian and degree columns differ by up to ~0.01 deg beyond rounding in some rows (e.g.
  3S1 S2 sl 5 0.3915 rad vs 22.4206 deg); both copied as printed.

## Not transcribed

- CR-159714 Appendix E manufacturing coordinates (sections on planes normal to the radial
  stacking line, 20/50/80 % span, every row of both rigs): PDF pp. 83-125 (printed 80-123).
- CR-159812 Appendix C (tabulated inlet and exit spanwise test data) and all performance maps:
  test data, not geometry.
- Appendix C/D symbol translation pages: PDF pp. 51-52 (Appendix C), 68 (Appendix D).

## Figure-only geometry (not digitized)

- CR-159714 Fig. 1 schematic (PDF p. 17): only the labelled numbers were taken (OD 0.61 m /
  24.0 in, ID 0.56 m / 21.95 in, station 9 axial positions); no blade-row axial positions.
- CR-159714 Fig. 2 blockage distribution (PDF p. 18); Figs. 7-24 spanwise solidity, t/c,
  metal angles, incidence, deviation, D-factor and loading for both rigs (PDF pp. 23-40).
- CR-159812 Fig. 5 axial locations of instrumentation planes (PDF p. 25): drawing without
  dimensions.

## Missing

- **Blade/vane counts are not printed** in either report. They could be derived from
  TAU/B and CHORD on the cone diameters (Appendix D), which is an interpretation step.
- **Axial positions of blade rows** (LE/TE axial coordinates) are not tabulated; Appendix D
  gives only cone diameters. Only station 9 position relative to rotor 1 LE (Fig. 1) is printed.
- Stagger angles: Appendix E headers may give them per manufacturing section (not read).
- Stator hub clearances / seal details: not given. Stators are cantilevered ("cantilevered
  stator assemblies", CR-159714 PDF p. 12).
- Per-row running tip clearances are not given; only the average (CR-159812 Table III).

## Other inconsistencies

- Design tip clearance 0.033 cm (0.013 in) in both reports; measured average running clearance
  0.0366 cm (3S1) and 0.0427 cm (3S2) in CR-159812 Table III, rounded to 0.037 / 0.043 cm in
  its text (PDF p. 15). The catalogue's "0.033-0.043 cm" spans design to measured.
- CR-159714 Table I, AMAC tip clearance in inches printed with a damaged glyph "(^ 010)",
  recorded `0.025 (0.010?)`.
- CR-159812 Table II, station 9 four-element Po rakes: two angles unreadable (`?`), two
  partially readable (`156.3?`, `269.9?`). Degree signs are dropped in the CSV (units row DEG).

## Appendix C (airfoil aerodynamic summary) conventions and doubtful cells

Conventions used in all 56 `CR159714_appC_*` files:
- The tangential-velocity symbol is printed as V followed by a theta glyph (V-theta-1,
  V-theta'-1); it is written `VO-1`, `VO-2`, `VO'-1`, `VO'-2` in every file (the six 3S1
  R3/S2/S3 files that used `VTHETA` were renamed). Printed `I` in labels and titles (e.g.
  `3SI`, `WCI/AI`) is read as digit 1 where it stands for 1.
- EPSI units are written `RADIAN` (SI block) and `DEGREE` (English block), as printed
  (`3S2_IGV_1` had `RADIANS`; p. 60 prints `RADIAN`, fixed).
- Each file has row 1 = headings, row 2 = units. In block 2 (angles/Mach/loss) the second
  header line printed under the headings (`DEGREE`, `TOTAL`, `PO1`, `STAGE`, `TOT-STG`) is
  treated as the units row; in the overall files the qualifier lines under each heading
  (`INLET`, `STAGE`, `ROTOR`) are joined to the heading and the unit line forms row 2.
- IGV pages print the footnote `N/A = NOT APPLICABLE TO IGV`. N/A is printed once per column
  on the page; the CSV puts `N/A` in streamline 1 of that column and leaves the other rows
  blank.
- `3S1_R3_1`, last column: heading and values are cut off at the faded right edge of PDF
  p. 58; heading recorded as `(heading illegible)`, values `1.3?` (only the first digits are
  visible). By position it is the column that is PO/PO INLET on the other rotor pages.
- Pages 53-54 (3S1 IGV, R1) are 1-bit scans in which 8 can read as 3, 5, 6 or 9.
- Second read: pp. 53-56 by agent A (with V^2 = VM^2 + VO^2, SI/English unit and PO-chain
  checks); pp. 57-66 by earlier agents (with print checks). See `source.json`.

### Cells marked `?` (408 in total)

- `appC_3S1_IGV_1` (14): SL1 EPSI-1 `-0.0000?`; SL1 EPSI-2 `-0.0000?`; SL2 EPSI-1 `-0.0003?`; SL3 EPSI-1 `-0.0008?`; SL3 EPSI-2 `-0.0016?`; SL4 PO/PO `0.9985?`; SL6 EPSI-2 `-0.0008?`; SL7 PO/PO `0.9985?`; SL7 EPSI-2 `-0.0003?`; SL8 PO/PO `0.9985?`; SL8 EPSI-2 `0.0002?`; SL9 EPSI-2 `0.0008?`; SL11 EPSI-1 `0.0000?`; SL11 EPSI-2 `-0.0000?`
- `appC_3S1_IGV_2` (15): SL1 PO/PO `0.9985?`; SL2 LOSS-P `0.0168?`; SL2 PO2/ `0.9985?`; SL3 PO2/ `0.9985?`; SL4 D-FAC `-0.1268?`; SL4 PO2/ `0.9985?`; SL5 PO/PO `0.9985?`; SL6 PO2/ `0.9985?`; SL6 PO/PO `0.9985?`; SL7 PO2/ `0.9985?`; SL8 PO2/ `0.9985?`; SL9 PO2/ `0.9985?`; SL10 M-1 `0.2225?`; SL10 PO/PO `0.9985?`; SL11 PO2/ `0.9985?`
- `appC_3S1_IGV_3` (9): SL4 EPSI-2 `-0.084?`; SL5 EPSI-2 `-0.069?`; SL6 RHOVM-2 `18.82?`; SL7 EPSI-2 `-0.019?`; SL8 EPSI-1 `-0.098?`; SL8 EPSI-2 `0.014?`; SL9 EPSI-1 `-0.085?`; SL9 EPSI-2 `0.048?`; SL10 EPSI-1 `-0.058?`
- `appC_3S1_IGV_overall` (1): PO/PO STAGE `0.9985?`
- `appC_3S1_R1_1` (14): SL1 EPSI-1 `0.0000?`; SL1 EPSI-2 `0.0007?`; SL1 PO/PO `1.1135?`; SL2 EPSI-2 `0.0033?`; SL2 PO/PO `1.1240?`; SL4 PO/PO `1.1295?`; SL5 PO/PO `1.1290?`; SL6 PO/PO `1.1288?`; SL7 PO/PO `1.1289?`; SL8 PO/PO `1.1293?`; SL9 PO/PO `1.1285?`; SL10 PO/PO `1.1218?`; SL11 EPSI-2 `0.0000?`; SL11 PO/PO `1.1124?`
- `appC_3S1_R1_2` (48): SL1 B-2 `55.8?`; SL1 M-2 `0.3850?`; SL1 M'-1 `0.4071?`; SL1 DEV `22.36?`; SL1 D-FAC `0.5433?`; SL1 OMEGA-B `0.0385?`; SL1 LOSS-P `0.0146?`; SL1 %EFF-A `91.75?`; SL1 %EFF-P `91.87?`; SL2 M-2 `0.4002?`; SL2 %EFF-A `93.64?`; SL2 %EFF-P `93.75?`; SL3 OMEGA-B `0.0508?`; SL3 LOSS-P `0.0199?`; SL3 %EFF-A `95.56?`; SL3 %EFF-P `95.65?`; SL4 M-1 `0.2683?`; SL4 M'-1 `0.4188?`; SL4 M'-2 `0.2823?`; SL4 TURN `23.68?`; SL4 D-FAC `0.5261?`; SL4 PO2/ `1.1312?`; SL4 %EFF-A `96.31?`; SL4 %EFF-P `96.37?`; SL5 DEV `10.78?`; SL5 TURN `22.71?`; SL5 PO2/ `1.1307?`; SL5 %EFF-A `96.71?`; SL5 %EFF-P `96.77?`; SL6 PO2/ `1.1305?`; SL6 %EFF-A `95.64?`; SL6 %EFF-P `95.71?`; SL7 M-2 `0.3966?`; SL7 M'-1 `0.4296?`; SL7 %EFF-A `95.63?`; SL7 %EFF-P `95.69?`; SL8 %EFF-A `95.19?`; SL8 %EFF-P `95.27?`; SL9 D-FAC `0.5231?`; SL9 LOSS-P `0.0181?`; SL9 PO2/ `1.1302?`; SL9 %EFF-A `95.17?`; SL9 %EFF-P `95.25?`; SL10 PO2/ `1.1235?`; SL10 %EFF-P `93.27?`; SL11 OMEGA-B `0.0974?`; SL11 %EFF-A `89.52?`; SL11 %EFF-P `89.67?`
- `appC_3S1_R1_3` (13): SL1 V-1 `299.1?`; SL1 EPSI-1 `0.006?`; SL1 EPSI-2 `0.039?`; SL2 V-1 `298.4?`; SL2 RHOVM-1 `18.98?`; SL2 RHOVM-2 `19.48?`; SL2 EPSI-2 `0.188?`; SL3 EPSI-2 `0.014?`; SL4 RHOVM-1 `18.93?`; SL6 V-2 `446.0?`; SL9 V-1 `293.2?`; SL10 V-1 `292.2?`; SL11 EPSI-2 `0.0??`
- `appC_3S1_R1_overall` (1): EFF-P ROTOR `95.29?`
- `appC_3S1_R2_1` (6): SL1 PO/PO `1.2293?`; SL4 EPSI-2 `-0.0004?`; SL5 PO/PO `1.2498?`; SL9 EPSI-1 `0.0000?`; SL10 EPSI-2 `-0.0008?`; SL11 PO/PO `1.2336?`
- `appC_3S1_R2_2` (3): SL1 M'-2 `0.2085?`; SL4 PO2/ `1.1118?`; SL10 M'-1 `0.4082?`
- `appC_3S1_R2_3` (1): SL2 VM-2 `217.8?`
- `appC_3S1_R2_overall`: none
- `appC_3S1_R3_1` (26): SL1 VM-1 `48.3?`; SL1 RHOVM-1 `66.33?`; SL1 (heading illegible) `1.3?`; SL2 (heading illegible) `1.3?`; SL3 V'-1 `133.2?`; SL3 (heading illegible) `1.3?`; SL4 EPSI-1 `-0.0036?`; SL4 EPSI-2 `-0.0029?`; SL4 (heading illegible) `1.3?`; SL5 RHOVM-2 `104.24?`; SL5 EPSI-2 `-0.0032?`; SL5 (heading illegible) `1.3?`; SL6 U-2 `166.7?`; SL6 RHOVM-2 `104.09?`; SL6 EPSI-1 `-0.0036?`; SL6 (heading illegible) `1.3?`; SL7 EPSI-1 `-0.0035?`; SL7 (heading illegible) `1.3?`; SL8 VO-1 `48.8?`; SL8 (heading illegible) `1.3?`; SL9 V'-1 `141.8?`; SL9 EPSI-2 `-0.0028?`; SL9 (heading illegible) `1.3?`; SL10 (heading illegible) `1.3?`; SL11 EPSI-1 `0.0001?`; SL11 (heading illegible) `1.3?`
- `appC_3S1_R3_2` (28): SL1 B'-1 `66.64?`; SL1 TURN `20.81?`; SL1 OMEGA-B `0.0812?`; SL1 %EFF-A `93.64?`; SL2 B-1 `38.4?`; SL2 B-2 `59.3?`; SL2 OMEGA-B `0.0645?`; SL2 PO2/ `1.1065?`; SL3 M-1 `0.2485?`; SL3 M'-1 `0.3806?`; SL3 PO2/ `1.0990?`; SL3 %EFF-A `94.97?`; SL3 %EFF-P `95.03?`; SL5 DEV `7.98?`; SL5 PO2/ `1.0958?`; SL7 LOSS-P `0.0116?`; SL7 %EFF-A `96.09?`; SL8 M-2 `0.3483?`; SL8 M'-1 `0.4033?`; SL9 DEV `7.68?`; SL9 OMEGA-B `0.0469?`; SL9 %EFF-A `94.89?`; SL9 %EFF-P `94.97?`; SL10 LOSS-P `0.0182?`; SL11 B-2 `65.7?`; SL11 M-2 `0.3198?`; SL11 TURN `11.81?`; SL11 OMEGA-B `0.0845?`
- `appC_3S1_R3_3` (23): SL1 V-1 `222.0?`; SL1 EPSI-1 `-0.000?`; SL1 PCT TE `0.0000?`; SL2 PCT TE `0.1000?`; SL3 PCT TE `0.2000?`; SL4 EPSI-2 `-0.168?`; SL4 PCT TE `0.3000?`; SL5 EPSI-2 `-0.181?`; SL5 PCT TE `0.4000?`; SL6 VO-2 `328.8?`; SL6 PCT TE `0.5000?`; SL7 EPSI-1 `-0.198?`; SL7 PCT TE `0.6000?`; SL8 VO-2 `326.8?`; SL8 RHOVM-2 `21.08?`; SL8 EPSI-2 `-0.188?`; SL8 PCT TE `0.7000?`; SL9 U-2 `561.5?`; SL9 EPSI-2 `-0.162?`; SL9 PCT TE `0.8000?`; SL10 PCT TE `0.9000?`; SL11 EPSI-1 `0.006?`; SL11 PCT TE `1.0000?`
- `appC_3S1_R3_overall` (2): PO/PO INLET `1.3627?`; TO2/TO1 `1.0283?`
- `appC_3S1_S1_1` (8): SL4 PO/PO `1.1246?`; SL4 EPSI-2 `0.0038?`; SL5 PO/PO `1.1249?`; SL6 PO/PO `1.1249?`; SL10 PO/PO `1.1148?`; SL10 TO/TO `1.0364?`; SL10 %EFF-A `85.78?`; SL10 %EFF-P `85.99?`
- `appC_3S1_S1_2` (1): SL6 TO/TO `1.0369?`
- `appC_3S1_S1_3` (1): SL10 EPSI-2 `-0.138?`
- `appC_3S1_S1_overall`: none
- `appC_3S1_S2_1` (10): SL1 VM-2 `48.2?`; SL2 RHOVM-2 `85.65?`; SL3 V-2 `86.9?`; SL4 VM-1 `76.6?`; SL11 V-1 `118.6?`; SL11 VO-1 `106.9?`; SL11 RHOVM-1 `68.43?`; SL11 RHOVM-2 `67.85?`; SL11 %EFF-P `84.98?`; SL11 EPSI-1 `-0.0006?`
- `appC_3S1_S2_2` (6): SL2 INCM `-9.35?`; SL2 OMEGA-B `0.0649?`; SL3 M-2 `0.2484?`; SL3 LOSS-P `0.0189?`; SL4 INCM `-7.18?`; SL11 PO/PO `1.1093?`
- `appC_3S1_S2_3` (7): SL4 %EFF-P `92.05?`; SL4 EPSI-1 `0.108?`; SL7 PCT TE `0.6000?`; SL8 RHOVM-1 `20.57?`; SL9 %EFF-P `90.66?`; SL11 %EFF-P `84.98?`; SL11 EPSI-1 `-0.036?`
- `appC_3S1_S2_overall` (1): EFF-P STAGE `91.65?`
- `appC_3S1_S3_1` (1): SL5 RHOVM-2 `103.86?`
- `appC_3S1_S3_2` (1): SL9 TO/TO `1.0283?`
- `appC_3S1_S3_3` (2): SL6 %EFF-P `93.33?`; SL11 TO/TO `1.1038?`
- `appC_3S1_S3_overall`: none
- `appC_3S2_IGV_1` (10): SL1 EPSI-1 `-0.0000?`; SL1 EPSI-2 `-0.0000?`; SL3 EPSI-2 `-0.0016?`; SL4 EPSI-2 `-0.0015?`; SL5 EPSI-2 `-0.0013?`; SL7 EPSI-1 `-0.0019?`; SL7 EPSI-2 `-0.0004?`; SL9 EPSI-2 `0.0008?`; SL11 EPSI-1 `0.0000?`; SL11 EPSI-2 `-0.0000?`
- `appC_3S2_IGV_2` (1): SL1 LOSS-P `0.0164?`
- `appC_3S2_IGV_3` (1): SL10 EPSI-1 `-0.059?`
- `appC_3S2_IGV_overall`: none
- `appC_3S2_R1_1`: none
- `appC_3S2_R1_2` (1): SL4 B'-2 `33.82?`
- `appC_3S2_R1_3` (3): SL3 EPSI-1 `0.088?`; SL10 PCT TE `0.9000?`; SL11 U-2 `571.2?`
- `appC_3S2_R1_overall`: none
- `appC_3S2_R2_1` (4): SL1 PO/PO `1.2089?`; SL2 EPSI-2 `-0.0004?`; SL4 PO/PO `1.2285?`; SL6 EPSI-1 `-0.0008?`
- `appC_3S2_R2_2` (1): SL1 B'-1 `62.33?`
- `appC_3S2_R2_3`: none
- `appC_3S2_R2_overall`: none
- `appC_3S2_R3_1` (5): SL2 PO/PO `1.3245?`; SL3 V-1 `88.8?`; SL3 RHOVM-1 `98.53?`; SL9 EPSI-1 `-0.0019?`; SL9 EPSI-2 `-0.0023?`
- `appC_3S2_R3_2` (2): SL1 %EFF-P `93.83?`; SL2 B-1 `38.7?`
- `appC_3S2_R3_3` (3): SL6 EPSI-1 `-0.182?`; SL7 VO'-1 `-385.2?`; SL10 EPSI-2 `-0.084?`
- `appC_3S2_R3_overall`: none
- `appC_3S2_S1_1` (11): SL2 EPSI-1 `0.0038?`; SL2 EPSI-2 `0.0041?`; SL3 EPSI-2 `0.0047?`; SL5 EPSI-1 `0.0028?`; SL5 EPSI-2 `0.0026?`; SL6 EPSI-1 `0.0020?`; SL6 EPSI-2 `0.0015?`; SL9 %EFF-P `89.88?`; SL10 EPSI-2 `-0.0025?`; SL11 RHOVM-1 `87.06?`; SL11 EPSI-2 `0.0000?`
- `appC_3S2_S1_2` (4): SL2 M-2 `0.253?`; SL4 PO/PO `1.1163?`; SL6 %EFF-A `93.86?`; SL7 D-FAC `0.4893?`
- `appC_3S2_S1_3` (7): SL2 EPSI-1 `0.218?`; SL3 EPSI-2 `0.268?`; SL5 V-2 `308.3?`; SL7 %EFF-P `92.38?`; SL8 EPSI-2 `-0.059?`; SL10 V-1 `413.3?`; SL10 EPSI-1 `-0.086?`
- `appC_3S2_S1_overall` (1): WCORR INLET `4.79?`
- `appC_3S2_S2_1` (8): SL2 %EFF-P `87.88?`; SL2 EPSI-2 `0.0032?`; SL3 V-2 `88.8?`; SL4 PO/PO `1.2238?`; SL4 EPSI-2 `0.0042?`; SL8 EPSI-2 `0.0025?`; SL10 %EFF-P `88.10?`; SL11 %EFF-P `84.78?`
- `appC_3S2_S2_2` (11): SL1 M-2 `0.2042?`; SL1 TURN `18.13?`; SL1 PO/PO `1.0981?`; SL1 TO/TO `1.0308?`; SL1 %EFF-P `88.17?`; SL2 B-1 `58.2?`; SL2 B-2 `38.7?`; SL2 LOSS-P `0.0714?`; SL4 %EFF-P `92.20?`; SL8 OMEGA-P `0.0387?`; SL9 %EFF-P `91.08?`
- `appC_3S2_S2_3` (6): SL2 %EFF-P `87.88?`; SL3 EPSI-1 `0.086?`; SL7 EPSI-2 `0.185?`; SL8 EPSI-1 `0.088?`; SL9 EPSI-2 `0.089?`; SL10 %EFF-P `88.10?`
- `appC_3S2_S2_overall` (1): PO/PO STAGE `1.0981?`
- `appC_3S2_S3_1` (36): SL1 %EFF-P `86.18?`; SL2 VO-2 `48.5?`; SL2 RHOVM-1 `90.94?`; SL2 PO/PO `1.3183?`; SL2 %EFF-A `87.83?`; SL2 %EFF-P `88.30?`; SL2 EPSI-1 `0.0018?`; SL3 VO-2 `48.1?`; SL3 PO/PO `1.3253?`; SL3 %EFF-P `90.28?`; SL4 V-1 `124.0?`; SL4 V-2 `86.4?`; SL4 VO-2 `48.0?`; SL4 %EFF-P `91.80?`; SL4 EPSI-2 `0.0026?`; SL5 V-1 `123.0?`; SL5 V-2 `86.3?`; SL5 VM-1 `74.2?`; SL5 EPSI-1 `0.0029?`; SL5 EPSI-2 `0.0030?`; SL6 V-2 `86.1?`; SL6 EPSI-1 `0.0032?`; SL6 EPSI-2 `0.0034?`; SL7 EPSI-1 `0.0034?`; SL7 EPSI-2 `0.0035?`; SL8 EPSI-2 `0.0036?`; SL9 EPSI-2 `0.0031?`; SL10 VO-1 `98.4?`; SL10 RHOVM-1 `88.20?`; SL10 PO/PO `1.3205?`; SL10 %EFF-A `88.01?`; SL10 %EFF-P `88.47?`; SL10 EPSI-1 `0.0018?`; SL11 VO-1 `99.7?`; SL11 RHOVM-1 `68.91?`; SL11 PO/PO `1.3104?`
- `appC_3S2_S3_2` (31): SL1 M-1 `0.3303?`; SL1 TURN `18.91?`; SL1 D-FAC `0.6044?`; SL1 LOSS-P `0.0225?`; SL1 PO2/ `0.9948?`; SL1 PO/PO `1.0878?`; SL1 %EFF-A `88.24?`; SL1 %EFF-P `88.39?`; SL2 LOSS-P `0.0201?`; SL2 PO/PO `1.0864?`; SL3 M-1 `0.3532?`; SL3 LOSS-P `0.0172?`; SL3 %EFF-P `90.53?`; SL4 TURN `19.45?`; SL4 PO/PO `1.0844?`; SL4 %EFF-P `91.83?`; SL5 D-FAC `0.4782?`; SL6 M-1 `0.3483?`; SL6 %EFF-P `93.03?`; SL7 B-1 `52.8?`; SL7 TO/TO `1.0252?`; SL8 OMEGA-B `0.0383?`; SL8 %EFF-A `91.89?`; SL9 M-2 `0.2399?`; SL9 TURN `19.98?`; SL9 D-FAC `0.4851?`; SL9 %EFF-P `90.71?`; SL10 INCM `-5.83?`; SL10 PO/PO `1.0860?`; SL10 TO/TO `1.0268?`; SL10 %EFF-A `89.18?`
- `appC_3S2_S3_3` (18): SL1 V-1 `381.9?`; SL1 VO-1 `338.2?`; SL1 %EFF-P `86.18?`; SL2 RHOVM-2 `18.56?`; SL2 %EFF-P `88.30?`; SL2 EPSI-2 `0.100?`; SL5 EPSI-1 `0.168?`; SL6 EPSI-1 `0.185?`; SL7 EPSI-2 `0.203?`; SL8 V-1 `398.0?`; SL9 V-2 `278.3?`; SL9 EPSI-1 `0.168?`; SL9 EPSI-2 `0.179?`; SL10 V-1 `383.0?`; SL10 RHOVM-1 `18.06?`; SL10 %EFF-P `88.47?`; SL10 EPSI-2 `0.111?`; SL11 %EFF-P `85.40?`
- `appC_3S2_S3_overall` (1): EFF-P STAGE `91.03?`

### Print checks that fail (values copied as printed)

- 3S1 IGV: LOSS-P SL11 0.0120 breaks the spanwise trend (about 0.0183 expected).
- 3S1 R1: SL2 PO2/PO1 1.1257 and PO/PO 1.1240, SL3 1.1314 and 1.1297 disagree with the
  stator 1 chain (1.1249/1.1232 and 1.1309/1.1292).
- 3S1 R1: English RHOVM-1 SL4 18.93 vs SI 18.90 (converted).
- 3S1 S1: V-2 SL2 85.1 vs 85.16 from VM-2 and VO-2.
- 3S1 S1: TO/TO STAGE SL11 1.0350 vs 1.0351.
- 3S1 S1 overall: EFF-AD INLET/STAGE about 0.15-0.2 points above the value implied by the
  printed PR/TR.
- 3S1 R2: the %EFF columns fit the rotor-only PO2/PO1, not the inlet-based ratio.
- 3S1 R3 (PDF p. 58): faded right edge, last column illegible (see above).
- 3S2 S1 overall: WCORR INLET printed 4.79 kg/sec, while 9.47 lbm/sec = 4.29 kg/sec;
  recorded `4.79?`.
- 3S2 S1: RHOVM-1 SL11 SI 87.06 vs English 16.81 (= 82.07 kg/m2 sec); recorded `87.06?`.
- 3S2 R2: V-1 SL1 75.3 vs 76.3 from VM-1 and VO-1.
- 3S2 R2: B'-1 SL1 print ambiguous between 62.33 and 67.33; recorded `62.33?`.
- 3S2 S2: LOSS-P SL2 read `0.0714?`; the check (OMEGA-B and spanwise trend) suggests 0.0214.
- 3S2 S2: English RHOVM-2 SL9 20.24 vs SI 98.85 (= 20.25 lbm/ft2 sec).
- 3S2 S3: LOSS-P SL1-3 (`0.0225?`, `0.0201?`, `0.0172?`) are near guesses (damaged glyphs).
- 3S2 R3 overall: WC1/A1 SI 76.06 vs English 15.59 (= 76.12 kg/sec sqm).
