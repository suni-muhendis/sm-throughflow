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

## Measured performance (Table VI)

Table VI (overall performance, pdf p27-28, printed 25-26), all six speed
parts, from a 300-dpi render; every '?' cell and every cell failing a check
re-read at 600-1200 dpi. Files: `TMX3083_tableVI_overall_<NNN>pct.csv`
(readings as columns). Tables VII (rotor 52, pdf p29-57) and VIII (stator 52,
pdf p58-86) print one part per reading in the same order as Table VI; the
five 100-percent-speed parts (o)-(s) of each are transcribed (see "Blade-element
data at 100 percent speed" below).

**All measured data are for the stators at the 2-chord position** (pdf p8),
while Tables II-V and Fig. 1 give the 4-chord layout; the 2-chord stator
axial position is not tabulated.

### Readings

| Speed | Table VI part | Readings (printed order, high to low flow) | Table VII / VIII pages |
|---|---|---|---|
| 70 % | (a) | 2221, 2222, 2224, 2225 | p29-32 / p58-61 |
| 80 % | (b) | 2219, 2220, 2196, 2195, 2193 | p33-37 / p62-66 |
| 90 % | (c) | 2218, 2190, 2189, 2188, 2187 | p38-42 / p67-71 |
| 100 % | (d) | 2217, 2185, 2184, 2200, 2182 | p43-47 / p72-76 |
| 110 % | (e) | 2205, 2204, 2203, 2202, 2201 | p48-52 / p77-81 |
| 120 % | (f) | 2216, 2215, 2211, 2208, 2207 | p53-57 / p82-86 |

- Test procedure (pdf p7): surveys "over a range of weight flows from maximum
  flow to the near-stall conditions at speeds from 70 to 120 percent"; with
  the stator at the 2-chord position, five weight flows at every speed (Table
  VI prints four at 70 percent); nine
  radial positions. Stations, averaging (stator-exit total temperature
  mass-averaged and total pressure energy-averaged over nine circumferential
  positions; overall values mass- and energy-averaged radially) and the
  translation to the blade edges (reference 4 of the report, pdf p8) are the
  same as in the other Lewis fan reports. Flows and conditions corrected to
  standard day on the rotor-inlet conditions.
- Peak efficiency (pdf p9): rotor 0.911 and stage 0.872 at design speed, both
  at 34.92 kg/sec (reading 2185). Near-design flow 32.33 kg/sec (reading 2200):
  rotor pressure ratio 1.269, stage pressure ratio 1.242 against design 1.251,
  stage efficiency 0.866. Design: pressure ratio 1.25, efficiency 0.894,
  32.7 kg/sec (194.4 kg/sec/m2 of annulus area), tip speed 257.7 m/sec (pdf p5).
- Stall margin (pdf p9): "about 20 percent based on the weight flow and
  pressure ratio at stall and the peak efficiency point". The stall point is
  not tabulated: with 2185 as reference and the lowest-flow reading 2182 the
  margin is only 13.6 %, so stall lies at a lower flow than any tabulated
  reading. Stall weight flow was the last flow before stall while closing the
  valve in small increments (pdf p8).
- Design speed is about 9741 rpm (ROTATIVE SPEED / PERCENT OF DESIGN SPEED
  97.35-97.46 on every reading).

### Checks (a check never overrode a clear print)

Efficiencies from the pressure and temperature ratios (within the rounding of
the 3-decimal temperature ratio); annulus/frontal flow ratio 1.1929-1.1930 and
orifice/frontal flow ratio 0.2004-0.2005 on every reading; rotative speed over
percent speed; head-rise coefficient over (PR^(0.4/1.4) - 1), times
(percent speed/100)^2, 4.34-4.38 on every reading.

### Cells marked '?' and print errors (Table VI)

| File | Reading | Row | Value | Note |
|---|---|---|---|---|
| 070pct | 2221 | WT FLOW AT STATOR OUTLET | `27.88?` | middle digit hidden by a blot; no check |
| 070pct | 2221 | ROTATIVE SPEED | `6827.1?` | fourth glyph a slanted stroke (7?); 6824.1 would also pass the speed check |
| 070pct | 2224 | STAGE HEAD RISE COEFFICIENT | `0.265` | middle digit damaged, 6-like; head-rise check excludes 0.255 and 0.285 |
| 070pct | 2225 | WT FLOW PER UNIT ANNULUS AREA | `121.32` | last digit damaged; 101.70 x 1.19295 = 121.32 |
| 080pct | 2196 | FLOW COEFFICIENT | `0.744?` | last digit damaged; the flow trend gives about 0.744-0.745 |
| 090pct | 2189 | WT FLOW AT ROTOR OUTLET | `31.21?` | last digit damaged; no check |
| 090pct | 2187 | FLOW COEFFICIENT | `0.631?` | first decimal damaged; the flow trend gives about 0.629-0.631 |
| 090pct | 2187 | WT FLOW AT ROTOR OUTLET | `27.32?` | printed as "27 3?", point and last digit damaged; no check |
| 100pct | 2217 | WT FLOW PER UNIT ANNULUS AREA | `211.53` | leading digits damaged; 177.32 x 1.19295 = 211.53 |
| 100pct | 2200 | FLOW COEFFICIENT | `0.713?` | middle digit illegible even at 1200 dpi |
| 100pct | 2200 | WT FLOW PER UNIT FRONTAL AREA | `161.30` | middle digits damaged; annulus ratio gives 161.31, orifice ratio 161.29 |
| 120pct | 2207 | ROTOR HEAD RISE COEFFICIENT | `0.514` | **print error**: clearly printed 0.514, but the head-rise check gives 0.313 (the other 29 readings agree within 0.5 %); kept as printed |

## Blade-element data at 100 percent speed (Tables VII-VIII)

Parts (o)-(s), readings 2217, 2185, 2184, 2200, 2182 (Table VII pdf p43-47,
Table VIII pdf p72-76, printed 41-45 and 70-74). Files:
`TMX3083_tableVII_rotor52_reading<N>.csv`,
`TMX3083_tableVIII_stator52_reading<N>.csv`. Read cell by cell from
native-resolution crops of each block. Format as in TM X-3101: four blocks
joined on RP, RP 1-9 only, INCIDENCE MEAN and SS, PEAK SS MACH NO, no units
row; stator WHEEL SPEED and EFF printed '0.'.

### Checks (a check never overrode a clear print)

- Every row: |V| and |W| from the components, absolute and relative angles,
  relative and meridional Mach numbers from the absolute Mach number, MERID
  VEL R; rotor EFF from the pressure and temperature ratios; stator LOSS COEFF
  TOT from the pressure ratio and inlet Mach number; stator absolute and
  relative columns identical. All ten tables pass.
- Rotor U/r gives the Table VI rotative speed of each reading (e.g. 2182:
  9789.3 rpm, U/r 10.251 per second x 100).
- Blade angles implied by REL BETAM IN - INCIDENCE MEAN and REL BETAM OUT -
  DEV agree across the five readings within 0.1 deg at every RP and with KIC
  and KOC of Tables IV and V (e.g. rotor RP5 36.0-36.1 / 11.5 against 36.05 /
  11.51; stator RP5 25.7-25.8 / -5.7 to -5.8 against 25.78 / -5.75). Solidity
  implied by D-FACT is constant across readings at every RP.
- Rotor outlet total pressure and temperature (inlet value times ratio)
  equal the stator inlet values within 0.01 N/cm2 and 0.2 K.
- Stator TOTAL TEMP RATIO is printed 0.993-1.000 (not 1); as printed, as in
  TM X-3101.

### Reading notes

- Rotor 2182 RP9 RADII OUT: the glyphs read "10.376" with the left half of
  the 8 lost; every other reading prints 10.876 and U/r requires 10.876
  (111.6 / 10.376 would give 10.76 against 10.25), so 10.876 is written.
- Rotor 2182 RP1 REL BETAM OUT: the 6 of 36.1 is broken ("3C.1"); the
  triangle gives 36.08.
- Stator 2217 RP5 TANG VEL IN: 118.8 (the third glyph is an 8 like the one
  after the point; 119.8 would contradict |V| = 260.0 and ABS BETAM IN 27.2).
- Stator 2217 RP4 REL VEL IN: the 8 of 258.2 is broken; stator relative and
  absolute values are equal.
- The rotor readings 2217, 2185 and 2184 were first read by an earlier pass;
  they pass every check above and were not re-read cell by cell.
