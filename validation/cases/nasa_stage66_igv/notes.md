# Stage 66 with IGV (NASA TM X-3345) - transcription notes

Source: Urasek, Steinke and Lewis, *Performance of Inlet Stage of Transonic
Compressor*, NASA TM X-3345, February 1976, NTRS 19760009935.

## Numbering
The report's own text: "The stage, designated stage 66 (inlet guide vanes,
rotor 66, stator 66)" (pdf p4). Table I is titled "STAGE 66"; the overall
performance figure calls it "STAGE 66-66"; Table VI calls it "STAGE 1" and
Table IX "STATOR 1" (it is the first stage of a five-stage core compressor).

## What exists and what does not
- Table I (design overall), Table II (rotor 66 design blade elements),
  Table III (stator 66 design blade elements), Table IV (rotor 66 geometry),
  Table V (stator 66 geometry): transcribed.
- Figure 1 flow-path coordinate box: transcribed (`TMX3345_fig1_flowpath.csv`).
- Figure 2 IGV: coordinate table (Z, Yp, Ys) and list of IGV data transcribed.
- **No design blade-element or blade-geometry table exists for the IGV.** The
  IGV is described only by Figure 2 (one section, no radial variation given,
  no stagger/metal-angle table) and the text on pdf p5. Tests were run with the
  vanes aligned axially. The IGV axial position is given only by the text
  spacing (IGV hub TE to rotor hub LE 2.50 cm) and graphically in Fig. 1.
- Measurement stations 0-3: axial positions shown only graphically in Fig. 1
  ("figure only"; no numbers printed). Station definitions in appendix A.
- Figures 3-6 (facility, hardware photos, probe, circumferential locations):
  figure only.

## Conventions stated in the report
- Tables carry no units; appendix C gives them: radii and axial dimensions in
  cm, angles in deg, velocities in m/sec, temperatures in K, pressures in
  N/cm2. Table I lines have no units printed either (weight flow kg/sec,
  flow per area (kg/sec)/m2, tip speed m/sec, RPM).
- BETAM = meridional air angle; beta = angle between air velocity and axial
  direction. K (kappa) angles KIC/KTC/KOC = angle between blade mean camber
  line (at LE / transition point / TE) and the meridional plane. SETTING ANGLE
  = angle between aerodynamic chord and meridional plane. No explicit sign
  rule is printed beyond this; signs appear as printed (e.g. stator KOC
  negative, IGV/stator exit BETAM printed `0.` / `-0.`).
- PERCENT SPAN = "percent of blade span from tip at rotor outlet" (also used
  for the stator rows).
- Blade elements lie on conical surfaces (CONE ANGLE column = angle between
  axial direction and the conical surface), stacked through the centers of
  gravity.
- Axial reference: appendix A says "Z axial distance referenced from rotor blade
  hub leading edge"; appendix C says ZIC/ZMC/ZTC/ZOC are "axial distance ...
  from inlet". In Table IV the rotor HUB ZIC is 0.000, so the table datum is
  the rotor hub leading edge. Check: rotor HUB ZOC 3.450 to stator HUB ZIC
  6.109 = 2.659, matching the text "2. 66 centimeters".
  The Fig. 1 flow-path box uses a different origin (Z = 0.000 far upstream):
  the inner radius 12.700 at Z = 30.480 equals rotor HUB RI 12.700, which
  suggests (not stated) that the rotor hub LE sits at Fig. 1 Z = 30.480.
- Columns in multi-block tables were merged: the CSV header is the printed
  group heading followed by the printed sub-heading (e.g. `RADII IN`,
  `LOSS COEFF TOT`); `MERID VEL R` and `PEAK SS MACH NO` are the two printed
  heading lines of those columns combined.

## Cells marked '?'
- Table II, HUB, INCIDENCE MEAN `6.8?`: the second digit is damaged (reads
  like 8; text layer gives "6.C").
- Table IV, row 8, DELTA INC `6.08?`: last digit looks like 8 but is damaged
  (text layer gives 6.06).
- Table V, row 7, TOTAL CAMBER `43.39?`: last digit damaged. KIC - KOC =
  35.86 - (-7.53) = 43.39 supports the reading.

## Oddities in the print (transcribed as printed, not corrected)
- Table V stator CONE ANGLE: TIP `2.507` (positive, while rows 1-2 are
  negative) and HUB `10.909` (row 11 is 13.652). Both clearly printed.
- Table V TIP thicknesses TI 0.065, TO 0.067 (all other rows TI = TO).
- Table V HUB AERO CHORD 3.702 is smaller than row 11 (3.743).
- IGV: Fig. 2 states blade chord 5.95 cm but the coordinate table runs Z = 0
  to 6.0960; at Z = 6.0960 Yp = +0.0038 and Ys = -0.0038 (sign cross). The
  printed profile is symmetric (Yp = -Ys at every station), i.e. the table
  is a thickness distribution about a straight line, although the text says
  multiple circular-arc profile. Trailing edge radius 0.2098 cm is larger than
  the leading edge radius 0.0596 cm as printed.
- Text: "One IGV blade passage is 13. 87°" while 360/26 = 13.85.
- Table I rotor and stage total temperature ratio are both 1.168.
- Overall-performance section quotes design tip speed as 425 m/s (pdf p8)
  while design text says 426 m/s and Table I 425.426.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 3, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TMX3345_tableII_rotor66.csv | 15 | INCIDENCE MEAN | `6.8?` | `6.8` | INCIDENCE MEAN = INCIDENCE SS + DELTA INC = 0.1 + 6.68 = 6.73-6.83 over rounding (relation holds on rows 8-11); REL BETAM IN - KIC is not exact in this table (row 11: 6.70 vs printed 6.6) | 600-dpi zoom: second glyph has a closed upper loop with a broken lower-left (8, not 7); relation admits 6.8 |
| TMX3345_tableIV_rotor66.csv | 11 | DELTA INC | `6.08?` | `6.08` | DELTA INC = INCIDENCE MEAN - INCIDENCE SS = 6.1 - 0.0 (6.05-6.15) from Table II row 8 | 600-dpi read: 6.08 legible; relation agrees |
| TMX3345_tableV_stator66.csv | 10 | TOTAL CAMBER | `43.39?` | `43.39` | TOTAL CAMBER = KIC - KOC = 35.86 + 7.53 = 43.39 | 600-dpi read: 43.3 clear, last glyph a damaged 9; relation fixes 43.39 |
