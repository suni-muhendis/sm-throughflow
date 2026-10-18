# Stage 53 (NASA TP-1299) - transcription notes

Source: Osborn, Moore and Steinke, *Aerodynamic Performance of a
1.35-Pressure-Ratio Axial-Flow Fan Stage*, NASA TP-1299, 1978, NTRS
19790001851.

## Numbering
"fan stage 53" (pdf p5); tables "ROTOR 53", "STATOR 53"; Table I "STAGE 53-53".
No IGV.

## What was transcribed
Table I (design overall), Table II (rotor 53 design blade elements), Table III
(stator 53 design blade elements), Table IV (rotor 53 geometry), Table V
(stator 53 geometry), and the Fig. 1 flow-path coordinate box including the
three survey-plane positions. Figures 2-6 (facility, photos, probes,
circumferential locations): figure only.

## Conventions stated in the report
- Units are not printed in the tables; appendix C: radii and axial dimensions
  cm, angles deg, velocities m/sec, temperatures K, pressures N/cm2.
- Leading zeros are omitted in this report's print (`.495`, `.0`); kept as
  printed.
- beta = angle between air velocity and axial direction; K (kappa) angles =
  angle between blade mean camber line and the meridional plane; SETTING
  ANGLE = angle between aerodynamic chord and meridional plane. Signs as
  printed (rotor KOC negative near the hub, stator KOC negative).
- PERCENT SPAN is from the tip at the rotor outlet.
- Blade elements are on conical surfaces approximating stream surfaces
  (CONE ANGLE column), stacked on a radial line through the centers of gravity.
- Axial reference: Z (Fig. 1 and appendix A) is measured from the rotor blade
  hub leading edge. Appendix C defines ZI/ZMC/ZTC/ZO as "axial distance from
  inlet hub to ..."; rotor HUB ZI = .000, so the same datum. Check: rotor HUB
  ZO 5.135 to stator HUB ZI 25.671 is 20.536 = 4 x 5.134, matching "four times
  the rotor hub chord" (axial projection).
- Survey planes (Fig. 1, footnote a): station 1 Z = -2.408, station 2
  Z = 7.727, station 3 Z = 32.492 cm. Data were translated to blade edges.
- DCA blades: ZMC = ZTC in every row, TURNING RATIO 1.000 throughout.
- No part-span damper is mentioned in this report.

## Cells marked '?'
- Table II row 2, MERID MACH NO IN `.549?`: last digit damaged (looks like 7
  or 9). ABS MACH NO IN in the same row reads .549 and there is no inlet swirl,
  so the meridional and absolute Mach numbers should be equal.
- Table III row 8, STREAMLINE SLOPE IN `5.07?`: middle digit damaged (0 or 8;
  text layer "5.C7").
- Table III HUB, PERCENT SPAN `100.00?`: printed glyphs look like "108.00"
  (damaged); the hub is 100 percent span by definition.
- Table V HUB, SETTING ANGLE `18.69?`: the 6 is partly broken.

## Oddities (transcribed as printed)
- Text says rotor t/c varies from 0.03 at the tip, but Table IV tip
  TM/AERO CHORD = .207/5.163 = 0.040 (hub .412/5.142 = 0.080 matches).
- Table V stator ZMC for rows 9 and HUB: the leading "2" is partly broken in
  print (27.892, 27.886); the ZTC column prints the same values clearly and
  ZMC = ZTC in every other row, so they were not marked '?'.
- Table I gives rotor PR 1.373 and stage PR 1.351; the text rounds to 1.35.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 3, still '?' 1, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP1299_tableIII_stator53.csv | 11 | STREAMLINE SLOPE IN | `5.07?` | `5.07?` | no exact relation; the radial trend (5.85 at 85 %, 5.73 at 95 %, 5.57 hub) favours 5.87, the glyph favours 0 | 600-dpi zoom: middle glyph is C-shaped (0 with a gap on the right, no waist of an 8); print and trend disagree, still uncertain, kept |
| TP1299_tableIII_stator53.csv | 13 | PERCENT SPAN | `100.00?` | `100.00` | the HUB row is 100 % span by definition (Table V HUB PERCENT SPAN 100.; rotor tables print 100.00) | 600-dpi read: second glyph looks like 8 (108.00) from a filled-in 0; value 100.00 |
| TP1299_tableII_rotor53.csv | 5 | MERID MACH NO IN | `.549?` | `.549` | VTH IN = 0, so MERID MACH IN = ABS MACH IN = .549 (MERID VEL IN = ABS VEL IN = 181.5) | 600-dpi read: last digit broken (7/9-like); exact relation fixes .549 |
| TP1299_tableV_stator53.csv | 13 | SETTING ANGLE | `18.69?` | `18.69` | no exact relation; radial trend 15.76, 16.59, 17.53, 18.69 | 600-dpi zoom: reads 18.69 with a thin but complete 6 |

## Measured performance (Table VI)

Table VI (overall performance, pdf p26-27, printed 23-24), all six speed
parts. Files: `TP1299_tableVI_overall_<NNN>pct.csv` (readings as columns; the
print has parameters as rows under a first row 'READING NUMBER'). Tables VII
(rotor 53, pdf p28-56) and VIII (stator 53, pdf p57-85) print one part per
reading, (a)-(cc), in the same order as Table VI; the six 100-percent-speed parts (r)-(w) are
transcribed (see "Blade-element data at 100 percent speed" below).

### Readings

| Speed | Table VI part | Readings (printed order, high to low flow) | Table VII / VIII pages |
|---|---|---|---|
| 70 % | (a) | 3027, 3028, 3029, 3030, 3031 | p28-32 / p57-61 |
| 80 % | (b) | 3011, 3012, 3014, 3015, 3007, 3006 | p33-38 / p62-67 |
| 90 % | (c) | 3016, 2997, 2998, 2999, 3000, 3001 | p39-44 / p68-72, p74 |
| 100 % | (d) | 3017, 2996, 2993, 2994, 2995, 3026 | p45-50 / p73, p75-79 |
| 110 % | (e) | 3023, 3024 | p51-52 / p80-81 |
| 120 % | (f) | 3038, 3039, 3040, 3042 | p53-56 / p82-85 |

In Table VIII the pages of parts (q) (reading 3001, pdf p74) and (r)
(reading 3017, pdf p73) are bound in swapped order.

- Peak efficiency (pdf p9): "The stage peak efficiency of 0.879 occurred at
  design weight flow (32.7 kg/sec)"; abstract (pdf p4): "at a pressure ratio of
  1.329 and design flow ... At design speed and flow the rotor efficiency was
  0.94". This is reading 2993 (orifice 32.71, stage PR 1.329, stage eff 0.879,
  rotor eff 0.940).
- Stall margin (pdf p9): "approximately 14 percent, based on weight flow and
  pressure ratio at peak efficiency and stall conditions". With 2993 as
  reference and the lowest-flow reading 3026 the margin is 12.9 %, so the
  stall point lies below the lowest tabulated flow; it is not tabulated.
- Data translated from the three survey planes to the blade edges (pdf p9);
  nine radial positions per flow (pdf p8).
- Design speed is about 11455 rpm (ROTATIVE SPEED / PERCENT OF DESIGN SPEED
  114.53-114.65 on every reading).

### Checks

Efficiencies from the pressure and temperature ratios (within the rounding of
the 3-decimal temperature ratio); annulus/frontal flow ratio 1.1934-1.1936 and
orifice/frontal flow ratio 0.2000-0.2001 on every reading; rotative speed over
percent speed; head-rise coefficient over (PR^(0.4/1.4) - 1), times
(percent speed/100)^2, 3.13-3.17 on every reading. No cell marked '?'.

### Oddities (as printed)

- ROTOR TEMP. RISE EFFICIENCY above 1 at 70-90 percent speed (up to 1.026,
  reading 3028); the printed pressure and temperature ratios give the same
  values, so these are measured values, not misreadings. Rotor efficiencies
  near and below about 80 percent speed are unreliable for comparison: the
  rotor temperature rise there is only 3-6 percent.
- Reading 2997: WT FLOW AT ROTOR INLET 31.69 against 31.94 at the orifice
  (other readings differ by less than 0.1); as printed.

## Blade-element data at 100 percent speed (Tables VII-VIII)

Parts (r)-(w), readings 3017, 2996, 2993, 2994, 2995, 3026 (Table VII pdf
p45-50; Table VIII pdf p73 and p75-79). Files:
`TP1299_tableVII_rotor53_reading<N>.csv`,
`TP1299_tableVIII_stator53_reading<N>.csv`. The continuation pages print only
"TABLE VII. - Continued." / "TABLE VIII. - Continued." and the part line.
Same format as TM X-3083: four blocks joined on RP, RP 1-9 only, INCIDENCE
MEAN and SS, PEAK SS MACH NO, no units row; stator WHEEL SPEED and EFF printed
'0.'. The scan is faint, and in this typeface 3 and 5 are easily confused;
every such cell was settled by a check where one exists (listed below).

### Checks (a check never overrode a clear print)

- Every row: |V| and |W| from the components, angles, Mach-number ratios,
  MERID VEL R; rotor EFF from the pressure and temperature ratios; stator LOSS
  COEFF TOT from the pressure ratio and inlet Mach number; stator absolute and
  relative columns identical.
- Rotor U/r gives the Table VI rotative speed of each reading.
- Blade angles implied by INCIDENCE MEAN/SS and DEV agree across the six
  readings within 0.1 deg at every RP; rotor values match KIC/KOC of Table IV
  within 0.2 deg. Stator values sit 0.0-0.35 deg from KIC/KOC of Table V (the
  same offset in every reading). Solidity implied by D-FACT is constant across
  readings.
- Rotor outlet total pressure and temperature (inlet value times ratio)
  equal the stator inlet values within 0.02 N/cm2 and 0.2 K at every RP.
- Stator TOTAL TEMP RATIO is printed 0.995-1.004; as printed.

### Reading notes

Cells settled by a check (glyph damaged or 3/5 ambiguous; value written
without '?'):
- Rotor 3017 RP2 TOTAL PRESS IN 10.13 (first pass `10.15?`): the stator inlet
  pressure 13.50 = 10.13-10.14 x 1.332 excludes 10.15; last glyph 3-shaped.
- Rotor 2993 RP7 ABS MACH NO OUT 0.669: the last glyph is a 3 or broken 9;
  M x W/V, M x Vm/V and the static temperature all give 0.669.
- Rotor 2994 RP1 EFF 0.838: the middle glyph reads 3 or 5; the pressure and
  temperature ratios (both confirmed by the stator inlet values) give
  0.836-0.843, not 0.858.
- Rotor 2995 RP6 TANG VEL OUT 143.3 (|V| = 211.7 excludes 145.3).
- Stator 2995 RP1 and RP4 D-FACT 0.336 and 0.332: the second digit is the
  same glyph as in 0.311 and 0.319 of the same column; the solidity implied
  by D-FACT in the other readings gives 0.336 and 0.333.
- Stator 3026 RP7 TOTAL TEMP IN 309.8 (broken 8; the rotor outlet gives
  309.7).

Cells kept with '?':
- Stator 2993 RP7 TANG VEL IN `144.1?` (last digit illegible; |V| and Vm give
  144.08).
- Stator 2993 RP1 and RP2 PEAK SS MACH NO `0.911?`, `0.861?` (last digits
  faint; no check).

As printed although inconsistent:
- Stator 2993 RP9: TOTAL PRESS RATIO 0.946 and LOSS COEFF TOT 0.255 are both
  clearly printed, but the ratio and inlet Mach number give a loss
  coefficient of 0.235 (0.255 would need a ratio of 0.941). The stator inlet
  pressure agrees with the rotor, so the ratio is taken as correct.
- Rotor 3026 RP9 WHEEL SPEED 129.2 / 129.9: U/r is 0.5 % below the other rows
  (the other readings print 129.8-129.9 / 130.5-130.7), but REL VEL and REL
  BETAM of the same row are computed with these values, so they are as printed.
- The rotor readings 3017 and 2996 were first read by an earlier pass; they
  pass every check above and were not re-read cell by cell, except the cell
  noted above.
