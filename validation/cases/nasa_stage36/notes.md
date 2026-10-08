# NASA Stage 36 (Rotor 36 / Stator 36)

Sources: NASA TP-1974 (performance report, Tables I-III, Fig. 1) and NASA TP-1337 (design report,
Tables I-II, Fig. 1). See source.json.

## Specific notes

- Blade counts 48 rotor / 62 stator.
- Tip clearance (TP-1974 p4 pdf): nominal nonrotating 0.071 cm; estimated running clearance 0.018 cm at
  design conditions (from calculated blade and disk growth). In scalars.json.
- TP-1974 Table III is a landscape page with rotor (a) and stator (b) side by side.

## Reading notes (cells marked '?' and print defects)

- TP1974 Table II(a) rotor 36 (pdf p15): row 8 TOTAL PRESS IN printed '10'.14' with a stray tick mark -> 10.14.
- TP1974 Table II(b) stator 36 (pdf p16): TIP TOTAL TEMP RATIO printed .998 (others 1.000) and TIP LOSS COEFF .061 (much lower than row 1 .087): both transcribed as printed.
- TP1974 Table III (pdf p17, landscape page, rotor and stator side by side; read at 400 dpi): rotor 36 row 5 PHISS printed with the top of the first digit missing ('c.10'), read 6.10? (neighbours 4.42 and 7.89). Stator 36 TIP CONE ANGLE printed -8.192 while row 1 is -5.168 (large jump; transcribed as printed). Stator 36 TIP TI .026 vs TO .025 (as printed).

## Conventions (stated in the reports)

- Units (Appendix C of the performance report): radii, thicknesses, axial dimensions and chord in cm;
  angles in deg; temperature K; pressure N/cm2; velocities m/sec. The CSVs leave the units row blank
  where the table prints no units.
- `Z` / `ZI`, `ZMC`, `ZTC`, `ZO`: axial distance referenced from the rotor-blade-hub leading edge
  (Appendix A: "Z axial distance referenced from rotor-blade-hub leading edge, cm"; Appendix C: "ZI axial
  distance from inlet hub to blade leading edge"). Rotor HUB ZI is .000. The flow-path boxes use the
  same origin ("Axial distance from rotor-blade-hub leading edge, cm").
- `KIC`, `KTC`, `KOC`: angle between the blade mean camber line (at LE, transition point, TE) and the
  meridional plane, deg. `SETTING ANGLE`: angle between aerodynamic chord and meridional plane.
  `DELTA INC`: difference between mean-camber and suction-surface blade angle at the LE.
  Flow angles `BETAM` are meridional air angles; `REL BETAM` relative to the blade.
- `CONE ANGLE`: angle between axial direction and the conical surface representing the blade element.
  Blade elements are defined on an unwrapped conical surface approximating the streamsurface
  (TP-1337 p14, pdf). Manufacturing sections are on planes normal to a radial line (TP-1337 p15).
- `PERCENT SPAN`: percent of blade span from the tip (at rotor outlet, per TP-1338 Appendix C).
  RP rows: TIP, 1..9, HUB = 0, 5, 10, 15, 30, 50, 70, 85, 90, 95, 100 % span.
- `TURN RATE`: ratio of the rate of blade-angle change per unit path distance of the front segment to
  that of the aft segment (1 = circular-arc meanline). `PHISS`: suction-surface camber ahead of assumed
  shock location. `CHOKE MARGIN`: (actual flow area - critical area)/critical area.
- Profile: MCA, two-segment meanline and surfaces, defined by KIC/KTC/KOC, TI/TM/TO and the axial
  positions ZMC (max thickness) and ZTC (transition point); elements stacked about their centres of area
  (TP-1337 p14). Detailed MCA definition: Crouse, NASA TN D-7345 (TP-1337 ref. 4), not transcribed.
- Measurement stations: station 1 upstream of the rotor, station 3 downstream of the stator; no
  measurement between rotor and stator. Station-2 data are translated from station 3 along design
  streamlines. Survey-plane axial positions are marked in the performance-report flow-path box (see
  below); the marks differ between reports.

## Flow path

- TP-1337 p12 (pdf): "The flow path geometry for all four stages is the same". TP-1337 Fig. 1 has one
  coordinate box shared by (a) stages 35/37 and (b) stages 36/38; (a) and (b) differ only in the drawn
  blade-row LE/TE positions. The catalogue's note that 36/38 have a different flow path is not correct
  for the walls. The TP-1337 box is copied into all four case folders; each performance report's own
  box is also transcribed, and all five boxes carry identical numbers.
- Survey-plane marks: TP-1659 marks outer -2.568, 4.445, 10.640 ("Survey planes"); TP-1974 marks outer
  -2.568 and 8.890 ("Survey planes") and 4.445 ("Calculation plane"); TP-2001 marks inner -2.568 and 8.890
  ("Instrumentation survey planes"); TP-1338 and TP-1337 boxes carry no marks. So station 3 is printed at
  10.640 cm in TP-1659 but 8.890 cm in TP-1974/TP-2001.
- The Table III TIP and HUB rows (RI/RO, ZI/ZO) give the wall points at each blade edge.

## Figure-only items (not digitized)

- TP-1337 Figs. 2-4 (design radial distributions), 5-7 (loss correlations, losses), 8-11 (coordinate
  systems and section nomenclature), 13 (rotor geometry parameters), 14 (rotor 37 blade-element
  profiles), 15 (stator geometry), 16 (Campbell diagrams), 18 (photographs), 20 (probe positions).
- Performance report Fig. 1 drawing (station positions only as drawn), Fig. 4-5 probes and circumferential
  layout.

## Not transcribed by instruction

- TP-1337 Appendix C blade manufacturing coordinates (inches, plane sections at constant radius, R1/R2
  LE/TE radii). pdf pages: rotor 35 p35-38, stator 35 p39-42, rotor 36 p43-49, stator 36 p50-53,
  rotor 37 p54-57, stator 37 p58-61, rotor 38 p62-68, stator 38 p69-72 (section nomenclature p34).
- Blade-element data at blade edges (Tables V and VI of each performance report) and overall
  performance (Table IV).

## Inconsistencies noticed across the four reports

- TP-1337 Table I prints stage 37 RPW as 17185.700; TP-1659 Table I and TM-107310 Table 1 give
  17188.7. Transcribed as printed in each.
- Stator 38 aspect ratio: 1.77 in TP-2001 Table I, TP-2001 text and title, and TP-1337 Table I; but
  TP-1337 text (p16 pdf) says "The aspect ratio is 1.78 for stators 36 and 38".
- TP-1337 p16 (pdf) prints "3.6 percent for rotors 36 and 36" (sic, meaning 36 and 38).
- TP-1337 Table II rotor first-mode/4E crossing speeds in the text (15 400, 11 000, 14 500, 12 500 rpm,
  p17 pdf) differ from the table's "Possible resonance rpm" (15 000, 11 000, 13 000, 12 000).
- Stator TIP rows of stages 36 and 38 show large jumps relative to row 1 (cone angle -8.192 vs -5.168;
  -8.087 vs -4.998; TIP loss coefficient .061 / .063 vs .087 / .091; TIP total-temperature ratio
  .998 / .997). All transcribed as printed.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 1, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP1974_tableIII_rotor36.csv | 8 | PHISS | `6.10?` | `6.10` | no exact relation; PHISS rises monotonically with span (4.42 at 30 %, 7.89 at 70 %), which excludes 8.10 and fits 6.10 at 50 % | 600-dpi zoom: first glyph is the lower half of a 6 (closed bottom loop with the left stem rising, top hook missing); a 0 would show a right side, an 8 a waist |
