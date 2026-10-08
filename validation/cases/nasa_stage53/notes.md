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
