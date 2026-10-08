# NASA two-stage fan with low-aspect-ratio first-stage rotor (NASA TP-1493)

Source: Urasek, Gorrell, Cunnan, NASA TP-1493 (AVRADCOM TR-78-49), 1979,
NTRS 19790018972. The first-stage rotor is the one later called Rotor 67
(TP-1493 does not use that name; see `../nasa_rotor67/`).

## What was transcribed

- `TP1493_tableI_overall.csv`: Table I, design overall parameters (fan, stage 1, stage 2).
- `TP1493_tableII_<row>.csv`: Table II, design blade-element parameters, all four rows
  (rotor1, stator1, rotor2, stator2), 13 radial positions each (TIP, 1-11, HUB).
- `TP1493_tableIII_<row>.csv`: Table III, blade geometry, all four rows.
- `TP1493_fig1_flowpath.csv`: the "Flow path coordinates" box of Fig. 1.

The Reid/Moore tables print three or four stacked blocks per row; each block
was merged into one CSV line per RP label. Column headings are
"<group heading> <sub heading>" as printed. No units are printed in the
tables; units come from appendix C (p20-21): radii, chord, thicknesses and
axial dimensions in cm; angles in deg; velocities in m/s; TOTAL TEMP in K;
TOTAL PRESS in N/cm^2. In Table III the BLADE ANGLES are printed in the order
KIC, KTC, KOC (kept in that order).

## Conventions stated in the report

- Z: axial distance referenced from the first-stage rotor-blade-hub leading edge, cm (appendix A, p15).
  Fig. 1 axis label: "Axial distance (from rotor-blade-hub-leading edge), Z, cm". Table III
  rotor-1 HUB ZI is printed `-.000`.
- PERCENT SPAN: "percent of blade span from tip referenced to first-stage-rotor outlet" (appendix C,
  p20, read from the image). The wording is ambiguous (each row's span positions appear to be its
  own streamline percentages; the phrase may mean the streamlines are defined by span fractions at
  rotor-1 outlet). Not interpreted here.
- Angles: BETAM = meridional air angle (angle between air velocity and axial direction; relative
  meridional angle based on cone angle, arctan(tan beta' cos alpha_c / cos alpha_s)). KIC/KTC/KOC =
  angle between blade-element mean camber line on the conical surface and the meridional plane at
  LE / transition point / TE. SETTING ANGLE = angle between aerodynamic chord on the conical surface
  and the meridional plane. TOTAL CAMBER = KIC - KOC. CONE ANGLE = angle between axial direction and
  the conical surface representing the blade element. Sections lie on cones (CONE ANGLE column).
- TM = thickness at maximum-thickness point, ZMC its axial location; ZTC = axial location of the
  transition point; TURNING RATIO = ratio of mean-camber-line curvatures upstream and downstream of
  the transition point; PHISS = suction-surface camber ahead of assumed shock location; CHOKE MARGIN =
  ratio of flow area greater than critical area to critical area; DELTA INC = difference between mean
  camber blade angle and suction-surface blade angle at LE.
- Design-point stator rows print ABS = REL values and WHEEL SPEED .0; EFF .000 for stators.
- Profiles: rotor 1 is multiple-circular-arc throughout (p4). Profile types of the other rows are not
  stated in TP-1493 (they are unchanged from TP-1314, see `../nasa_2stage_fan_tp1314/`).

## Rows unchanged from TP-1314

Only rotor 1 is new. "The other blade rows were unchanged (see ref. 2). The flow path of this fan,
also unchanged, is shown in figure 1" (p4). Ref. 2 = NASA TP-1314. The Fig. 1 flowpath box in this
report should therefore equal the TP-1314 Fig. 1 box; compare with `../nasa_2stage_fan_tp1314/`.
Rotor-1 LE moved forward and TE aft with the stacking line axially unchanged (p4).

## Flowpath box (Fig. 1, p121)

Read at 600 dpi. In the "Outer" column two vertical arrows replace values: one from the row
Z = 12.304 (24.384) down to Z = 20.803, and one from Z = 30.084 (23.622) down to Z = 42.784. The
arrow is a ditto mark (constant outer radius); those cells are transcribed as `↓`, not filled in.
The figure also shows the higher-aspect-ratio rotor outline (dashed, "ref. 2") and stations 1, 2, 3;
station axial positions are figure only (no numbers printed). Figure 3 (radial distributions of
design parameters of rotor 1, both versions) is figure only.

## Blade counts

TP-1493 does not print blade counts. Solidity x 2 pi r_mean / chord from Table III gives 22.0 (R1),
34.0 (S1), 38.0 (R2), 42.0 (S2) at every RP; this is a derived check, not a printed value. TP-2879
(Rotor 67 alone) prints 22 rotor blades.

## Clearance

Running (rotating) radial tip clearance calculated as 0.04 cm for both rotors (p6). No cold
clearance is given in TP-1493.

## Cells marked `?`

All are print defects where the intended digit is clear from context but the glyph is damaged:
- rotor1 Table II: RP 4 ABS BETAM IN printed `.C` (transcribed `.0?`); RP 3 ABS VEL IN last digit
  damaged (`188.0?`; MERID VEL IN = 188.0 and TANG VEL IN = .0).
- stator1 Table II: TIP ABS VEL OUT `174.8?` (second digit damaged); RP 8 REL BETAM IN `43.0?`
  (second digit damaged; ABS BETAM IN = 43.0); HUB WHEEL SPEED OUT `.0?` (damaged glyph).
- rotor2 Table II: MERID VEL IN at RP 4, 5, 6 (`196.9?`, `197.1?`, `195.6?`, first digits faint; equal
  to ABS VEL IN since TANG VEL IN = .0); RP 11 TOTAL PRESS IN `15.56?` (first digit damaged); RP 1
  INCIDENCE MEAN `2.5?`; RP 3 D-FACT printed without a visible decimal point (`.436?`).
- stator2 Table II: TIP STREAMLINE SLOPE OUT `-.03?`; RP 4 EFF `.000?`.
- stator1 Table III: HUB ZTC `13.928?` (9 faint); RP 3 TURNING RATIO `1.000?` (last digit damaged).
- stator2 Table III: RP 4 TO `.102?` (decimal point damaged).

## Plausibility checks run (none changed a value)

Velocity triangles (V^2 = Vm^2 + Vu^2, W, BETAM), Mach ratios, MERID VEL R = Vm_out/Vm_in,
U/r constant (16.80) for both rotors, Table III RI/RO equal Table II RADII, KIC - KOC = TOTAL CAMBER,
implied blade count constant along span. All passed within print rounding. Not checked: thicknesses,
axial dimensions, PHISS, choke margin (only by eye for smoothness).

## Not transcribed

Tables IV-VIII (overall performance), IX-XII (blade-element performance at blade edges): measured
data, outside this geometry step. Pages: IV-VIII p32-36; IX R1 p37-57, X S1 p58-78, XI R2 p79-99,
XII S2 p100-120.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 16, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP1493_tableIII_stator1.csv | 6 | TURNING RATIO | `1.000?` | `1.000` | all 12 other rows of the stator column print 1.000; glyph shape | 600-dpi zoom: last glyph is a 0 with its top-right stroke dropped out (no 6 top hook); stator turning ratio 1.000 on every other row |
| TP1493_tableIII_stator1.csv | 15 | AXIAL DIMENSIONS ZTC | `13.928?` | `13.928` | radial trend of ZTC (14.034, 13.987, 13.960, 13.928) | 600-dpi zoom: third digit is a 9 with a broken top loop; only 9 fits the monotone ZTC trend |
| TP1493_tableIII_stator2.csv | 7 | BLADE THICKNESSES TO | `.102?` | `.102` | TO = TI at rows TIP-4 (TI row 4 = .102) | 600-dpi zoom: digits 102 clear, decimal point smudged into a colon-like mark |
| TP1493_tableII_rotor1.csv | 6 | ABS VEL IN | `188.0?` | `188.0` | V^2 = VM^2 + VTH^2 with TANG VEL IN .0 and MERID VEL IN 188.0 (also ABS MACH IN .570 = MERID MACH IN .570) | 600-dpi zoom: 188 clear, tenths glyph broken; the exact relation fixes it to 188.0 |
| TP1493_tableII_rotor1.csv | 7 | ABS BETAM IN | `.0?` | `.0` | TANG VEL IN .0 gives ABS BETAM IN 0 (all other rows .0) | 600-dpi zoom: glyph is an open 0 (C-shaped dropout); value fixed by VTH = 0 |
| TP1493_tableII_rotor2.csv | 4 | INCIDENCE MEAN | `2.5?` | `2.5` | INCIDENCE MEAN = REL BETAM IN - KIC = 64.5 - 61.97 = 2.53 (Table III rotor 2 row 1) | 600-dpi zoom: 2. clear, tenths glyph broken but 5-shaped; relation gives 2.5 |
| TP1493_tableII_rotor2.csv | 6 | D-FACT | `.436?` | `.436` | Lieblein D = 1 - W2/W1 + (r2 VTH2 - r1 VTH1)/((r1+r2) sigma W1) = 0.4356 (W 418.0/283.6, VTH 0/134.8, r 22.002/21.814, solidity 1.407) | 600-dpi zoom: 436 clear, leading decimal point not printed; relation agrees |
| TP1493_tableII_rotor2.csv | 7 | MERID VEL IN | `196.9?` | `196.9` | VM = V with TANG VEL IN .0 (ABS VEL IN 196.9; MERID MACH IN .552 = ABS MACH IN .552) | 600-dpi zoom: degraded glyphs (1?6.9); exact relation fixes 196.9 |
| TP1493_tableII_rotor2.csv | 8 | MERID VEL IN | `197.1?` | `197.1` | VM = V with TANG VEL IN .0 (ABS VEL IN 197.1; Mach .553 = .553) | 600-dpi zoom: faint but reads 197.1; relation agrees |
| TP1493_tableII_rotor2.csv | 9 | MERID VEL IN | `195.6?` | `195.6` | VM = V with TANG VEL IN .0 (ABS VEL IN 195.6; Mach .549 = .549) | 600-dpi zoom: 9 broken, reads 195.6; relation agrees |
| TP1493_tableII_rotor2.csv | 14 | TOTAL PRESS IN | `15.56?` | `15.56` | stator-1 TOTAL PRESS IN x RATIO = 16.49 x .943 = 15.55 (same 0.01 offset as rows 9 and HUB: 15.91/15.92, 15.37/15.38) | 600-dpi zoom: leading 1 faint, 5.56 clear; relation agrees within rounding |
| TP1493_tableII_stator1.csv | 3 | ABS VEL OUT | `174.8?` | `174.8` | stator (U = 0): ABS VEL OUT = REL VEL OUT = 174.8 = MERID VEL OUT (TANG VEL OUT .0); ABS MACH OUT .478 = REL MACH OUT | 600-dpi read: middle digit damaged (17?.8); exact relations fix 174.8 |
| TP1493_tableII_stator1.csv | 11 | REL BETAM IN | `43.0?` | `43.0` | stator (U = 0): REL BETAM IN = ABS BETAM IN = 43.0 | 600-dpi read: second digit damaged (4?.0); exact relation fixes 43.0 |
| TP1493_tableII_stator1.csv | 15 | WHEEL SPEED OUT | `.0?` | `.0` | stator: wheel speed 0 (every other row .0) | 600-dpi read: open 0 glyph (dropout); stator wheel speed is 0 |
| TP1493_tableII_stator2.csv | 3 | STREAMLINE SLOPE OUT | `-.03?` | `-.03` | casing is cylindrical at the stator-2 exit (Fig. 1 outer radius 23.622 from Z = 30.084 to beyond 36.754; Table III RI = RO = 23.622 at TIP), so the tip slope must be near 0, which excludes -.83 | 600-dpi zoom: -.03 with a blotted 0; flowpath check confirms |
| TP1493_tableII_stator2.csv | 7 | EFF | `.000?` | `.000` | stator EFF is printed .000 on every other row of both stators | 600-dpi read: first 0 partly dropped out; value .000 |
