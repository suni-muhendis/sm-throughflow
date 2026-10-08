# NASA Stage 35 (Rotor 35 / Stator 35)

Sources: NASA TP-1338 (performance report, Tables I-III, Fig. 1) and NASA TP-1337 (design report,
Tables I-II, Fig. 1). See source.json.

## Specific notes

- Blade counts 36 rotor / 46 stator (TP-1338 p6 pdf; TP-1337 Tables I, II).
- Tip clearance: not stated in TP-1338 or TP-1337 (text search and rendered pages). Must be taken from
  elsewhere or assumed.
- TP-1338 Table I title is printed "FOR STAGE 35-35".

## Reading notes (cells marked '?' and print defects)

- TP1338 Table II(a) rotor 35 (pdf p25): print defects: TIP TOTAL PRESS IN printed '1C.14' (top of 0 broken) -> 10.14; row 1 REL BETAM IN '66.6' second 6 partly broken; row 3 TOTAL TEMP IN first 2 faint -> 288.2; row 4 REL BETAM OUT printed '54 0' and TOTAL TEMP RATIO '1 230' with decimal point not printed -> 54.0, 1.230; row 8 ABS VEL IN middle digit unreadable ('1?7.4'), transcribed 197.4? (MERID VEL IN of the same row reads 197.4 and ABS BETAM IN is .0); row 8 REL VEL IN third digit 3 or 8 -> 388.6?; row 2 LOSS COEFF TOT middle digit broken (6 or 3) -> .165?.
- TP1338 Table II(b) stator 35 (pdf p26): row 1 REL BETAM IN printed with the 9 broken ('3^.0'), transcribed 39.0? (ABS BETAM IN of the same row reads 39.0; for a stator relative = absolute); row 6 STREAMLINE SLOPE OUT printed '2.20' followed by a small stray mark (print artifact, not a digit); row 7 TOTAL TEMP RATIO 1.000 with the leading 1 partly broken.
- TP1338 Table III(a) rotor 35 (pdf p27): row 1 ZMC middle digit broken ('2.3?1', looks like 6) -> 2.361?; row 3 ZMC last digit printed like 'P' (top loop, open bottom; 8 or 9) -> 2.268?; row 6 CHOKE MARGIN clearly printed .059 although neighbours are .037 and .043 (transcribed as printed); TIP AERO CHORD 5.609 (6 slightly broken); HUB KTC 46.24 (decimal point faint).
- TP1338 Table III(b) stator 35 (pdf p28): row 4 ZMC 6.544 (first 5 partly broken); row 6 KOC 3.44 (second 4 partly broken); TIP KOC 2.52 has a stray mark after the 2.
- TP1338 Table I (pdf p24): row label 'AIRFLJW PER UNIT ANNULUS AREA' is printed with a typo (J for O); kept as printed. No units are printed in the table.
- TP1338 Fig. 1 (pdf p70) flow path coordinates box: outer-wall first axial distance printed '-22 860' (decimal point not printed) -> -22.860 (inner wall column reads -22.860). Transcribed from a 200 dpi render, re-checked at 400 dpi.

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

Resolved 5, still '?' 1, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP1338_tableIII_rotor35.csv | 4 | ZMC | `2.361?` | `2.361` | no exact relation; spans TIP-3 are equally spaced (0, 5, 10, 15 %) and 2.410, 2.361, 2.313 give equal steps (-0.049, -0.048); 2.331 or 2.381 would break the trend | 600-dpi zoom: middle glyph is a 6 with a broken upper stroke; trend agrees |
| TP1338_tableIII_rotor35.csv | 6 | ZMC | `2.268?` | `2.268?` | no exact relation; 2.268 and 2.269 both fit the trend | 600-dpi zoom: last glyph prints as 'P' (closed upper loop, open bottom, 8 or 9); still uncertain, kept |
| TP1338_tableII_rotor35.csv | 5 | LOSS COEFF TOT | `.165?` | `.165` | LOSS PARAM TOT = omega cos(REL BETAM OUT)/(2 sigma): .034 -> omega .160-.165 (beta' 56.4, sigma 1.324); .135 would give .028; trend .175, -, .157 | 600-dpi read: middle digit broken (6 or 3); relation excludes 3 |
| TP1338_tableII_rotor35.csv | 11 | ABS VEL IN | `197.4?` | `197.4` | V = VM with TANG VEL IN .0 (MERID VEL IN 197.4; ABS MACH IN .601 = MERID MACH IN .601) | 600-dpi read: middle digit unreadable (1?7.4); exact relation fixes 197.4 |
| TP1338_tableII_rotor35.csv | 11 | REL VEL IN | `388.6?` | `388.6` | W = sqrt(VM^2 + U^2) = sqrt(197.4^2 + 334.7^2) = 388.58; 383.6 excluded | 600-dpi read: third digit 3 or 8; relation fixes 388.6 |
| TP1338_tableII_stator35.csv | 4 | REL BETAM IN | `39.0?` | `39.0` | stator (U = 0): REL BETAM IN = ABS BETAM IN = 39.0 | 600-dpi read: 9 broken (3^.0); exact relation fixes 39.0 |
