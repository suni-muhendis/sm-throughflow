# Stage 52-52 (NASA TM X-3083) - transcription notes

Source: Moore and Steinke, *Aerodynamic Performance of a 1.25-Pressure-Ratio
Axial-Flow Fan Stage*, NASA TM X-3083, 1974, NTRS 19740026337.

## Numbering
"designated stage 52-52, with the rotor being rotor 52 and the stator being
stator 52" (pdf p4). No IGV. The catalogue listed the rotor blade count as
unknown; the text gives **30 rotor blades** and 34 stator blades (pdf p5).

## Scan quality
The PDF is a poor scan (Table II is stamped "REPRODUCIBILITY OF THE ORIGINAL
PAGE IS POOR"). Pages were rendered at 300 dpi (Fig. 1 at 400, one column at
600) and read in zoomed crops. The pdftotext layer is badly garbled here and
was used only to locate pages. As an extra check, the blade-element tables
were tested for internal consistency (V = sqrt(Vm^2 + Vu^2), W from U - Vu,
BETAM = atan(Vu/Vm), REL/MERID Mach = ABS Mach x W/V, Vm/V, MERID VEL R =
Vm,out/Vm,in; geometry TOTAL CAMBER = KIC - KOC). All rows pass within
rounding.

## Stator spacing (the point of this report)
- Tested with the stators at 1, 2 and 4 rotor tip chords downstream of the
  rotor trailing edge (pdf p3, p4).
- Fig. 1 and (apparently) the design geometry tables show the 4-chord
  position: "The stators are located 4 rotor chords downstream of the rotor in
  the figure." Table V stator ZI = 25.436 (tip) to 25.563 (hub) is the axial
  position in that layout.
- **All tabulated performance data (Tables VI-VIII) are for the 2-chord
  position** (pdf p8). The stator axial positions for the 1- and 2-chord
  configurations are not tabulated anywhere; only "1, 2, 4 rotor tip chords"
  is given. Instrumentation stations were the same for all three spacings.
- Not stated which "rotor tip chord" length is meant (aero chord 5.166 cm at
  the tip in Table IV; axial projection ZO - ZI at the tip = 3.642 cm). In the
  4-chord geometry, rotor TIP ZO 4.415 to stator TIP ZI 25.436 = 21.021 cm,
  and rotor HUB ZO 5.128 to stator HUB ZI 25.563 = 20.435 cm (about 4 x 5.1).

## Conventions
- Axial reference: Z from rotor blade hub leading edge (appendix A, Fig. 1
  axis). Appendix C calls ZIC... "from inlet"; tables print ZI/ZMC/ZTC/ZO and
  rotor HUB ZI is `-0.`, so the table datum is the rotor hub LE.
- PERCENT SPAN from the tip at rotor outlet; beta from axial; kappa angles to
  the meridional plane; setting angle chord to meridional plane. Stator
  REL BETAM equals ABS BETAM with the same sign (no rotation), so the sign
  convention is not stated for relative angles.
- Blade elements on conical surfaces (CONE ANGLE column).
- Measurement stations 1, 2, 3: positions only drawn in Fig. 1 (no numbers;
  figure only). Figures 2-6: figure only.
- No part-span damper mentioned; rotor blades pin mounted.

## Cells marked '?'
- Table II row 5, REL VEL OUT `188.4?` (6/8 ambiguous; the triangle
  sqrt(180.1^2 + (176.6-121.1)^2) = 188.5 supports 188.4).
- Table II row 6, REL VEL IN `248.1?` (second glyph damaged, "24E.1";
  triangle gives 248.1).
- Table III row 6, REL BETAM IN `34.9?` (looks like 9; ABS BETAM IN is 34.8
  and for a stator they should be equal, so the print may really say 34.9 or
  the glyph is a damaged 8).
- Table IV row 6, ZI `0.108?` (second glyph damaged).
- Table V CONE ANGLE rows 6, 7, 8, 9, HUB: `2.991?`, `3.499?`, `3.735?`,
  `3.580?`, `0.057?`. The left part of these cells is lost in the scan; the
  visible trailing digits are 991, 499, 735, 580, 57. Leading digits are
  guesses from the trend of rows TIP-5 (0.057 ... 2.228) and from the hub
  RI = RO (flat), and must be treated as unknown.
- Table V DELTA INC rows 7 and 8: `7.16?` (last digit damaged).

## Oddities (as printed)
- Table II HUB TOTAL PRESS RATIO 1.173 while the text says about 1.17 at the
  hub; consistent.
- Table I TIP SPEED 257.682 (the 6 is slightly damaged but clear).

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 7, still '?' 4, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TMX3083_tableII_rotor52.csv | 8 | REL VEL OUT | `188.4?` | `188.4` | W = sqrt(VM^2 + (U - VTH)^2) = sqrt(180.1^2 + (176.6 - 121.1)^2) = 188.46 (188.40-188.52 over rounding); W = V M'/M = 217.0 x .556/.640 = 188.5 +- 0.3; 186.4 excluded | 600-dpi zoom: 1, 8 and .4 clear, third glyph a 6/8 with a weak upper loop; relations fix 8 |
| TMX3083_tableII_rotor52.csv | 9 | REL VEL IN | `248.1?` | `248.1` | W = sqrt(VM^2 + U^2) = sqrt(200.6^2 + 146.1^2) = 248.16 (248.10-248.22 over rounding) | 600-dpi zoom: third glyph is a broken 8 (E-like); .1 clear; relation agrees |
| TMX3083_tableIII_stator52.csv | 9 | REL BETAM IN | `34.9?` | `34.8` | stator (U = 0): REL BETAM IN = ABS BETAM IN = 34.8; atan(VTH/VM) = atan(131.5/189.3) = 34.79 | 600-dpi zoom: last glyph is an 8 with its lower-left stroke dropped (reads like 9); the program prints relative and absolute stator angles from the same value, so the reading is corrected to 34.8 |
| TMX3083_tableIV_rotor52.csv | 9 | AXIAL DIMENSIONS ZI | `0.108?` | `0.108` | approximate: ZO - CHORD cos(SETTING) cos(CONE) = 5.068 - 4.958 = 0.110, offsets on rows 5 and 7 are 0.000-0.004; 0.408 or 0.708 excluded | 600-dpi zoom: second glyph is a thin broken 1 ('i'); reading 0.108 |
| TMX3083_tableV_stator52.csv | 9 | CONE ANGLE | `2.991?` | `2.991` | atan((RO-RI)/(ZO-ZI)) = atan(0.260/4.982) = 2.988 deg (relation reproduces rows 3-5 to 0.004) | 600-dpi zoom: .991 clear; the leading glyph is partly visible with a 2/3-like top; relation excludes 3 |
| TMX3083_tableV_stator52.csv | 10 | DELTA INC | `7.16?` | `7.16` | no exact relation; neighbours 7.18, -, -, 7.16, 7.16 | 600-dpi zoom: last glyph shows the top hook and left stem of a 6 with the loop partly dropped; reading 7.16 |
| TMX3083_tableV_stator52.csv | 10 | CONE ANGLE | `3.499?` | `2.499?` | atan((RO-RI)/(ZO-ZI)) = atan(0.217/4.957) = 2.51 deg, so the integer digit is 2, not 3 | 600-dpi zoom: '499' visible, leading digit and point lost in the scan; best reading changed to 2.499 by the relation but the digit is not legible, so '?' kept |
| TMX3083_tableV_stator52.csv | 11 | DELTA INC | `7.16?` | `7.16` | no exact relation; neighbours 7.18, -, -, 7.16, 7.16 | 600-dpi zoom: last glyph has the full left stem and closed bottom loop of a 6 (a 0 would have a full right side); reading 7.16 |
| TMX3083_tableV_stator52.csv | 11 | CONE ANGLE | `3.735?` | `1.735?` | atan((RO-RI)/(ZO-ZI)) = atan(0.150/4.952) = 1.74 deg, so the integer digit is 1, not 3 | 600-dpi zoom: '.735' visible, leading digit lost; best reading changed to 1.735 by the relation, '?' kept |
| TMX3083_tableV_stator52.csv | 12 | CONE ANGLE | `3.580?` | `0.580?` | atan((RO-RI)/(ZO-ZI)) = atan(0.059/4.948) = 0.68 deg (relation good to about 0.1 deg near the end walls: TIP and HUB print 0.057 with RI = RO), so the integer digit is 0 | 600-dpi zoom: '580' visible, leading digit lost; best reading changed to 0.580, '?' kept |
| TMX3083_tableV_stator52.csv | 13 | CONE ANGLE | `0.057?` | `0.057?` | RI = RO = 10.160 (flat hub), same as TIP (RI = RO, printed 0.057) and the rotor hub (0.057) | 600-dpi zoom: only '57' and a fragment visible; consistent with 0.057 but leading digits lost, '?' kept |
