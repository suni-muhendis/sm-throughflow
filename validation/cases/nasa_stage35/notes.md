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
- Blade-element data at blade edges (Tables V and VI) for the 80, 60 and 50 percent speed readings
  (parts (l), (r), (s)). Table IV (all speeds) and Tables V-VI at 100, 90 and 70 percent speed are
  transcribed; see "Measured performance (Tables IV-VI)" below.

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

## Measured performance (Tables IV-VI)

Transcribed from NASA TP-1338: Table IV (overall performance, pdf p29-31, printed 25-27), all six
speed parts; Table V (rotor 35, pdf p32-37, printed 28-33) and Table VI (stator 35, pdf p51-56,
printed 47-52), the six 100-percent-speed parts; the 90- and 70-percent-speed parts were added
later (see "Tables V-VI at 90 and 70 percent speed" below). Rendered at 300 dpi; second read at 400 dpi,
suspect cells at 600 dpi. Files: `TP1338_tableIV_overall_<NNN>pct.csv` (readings as columns),
`TP1338_tableV_rotor35_reading<N>.csv`, `TP1338_tableVI_stator35_reading<N>.csv`.

### Readings

| Speed | Table IV part | Readings (printed order) |
|---|---|---|
| 100 % | (a) | 4004, 3978, 3977, 3974, 3976, 3975 |
| 90 % | (b) | 3979, 3982, 3983, 3984, 3985 |
| 80 % | (c) | 3987 |
| 70 % | (d) | 3995, 3994, 3993, 3990, 3989 |
| 60 % | (e) | 3997 |
| 50 % | (f) | 4000 |

Tables V and VI print one part per reading, (a)-(s), in the same order as Table IV (100 % (a)-(f),
90 % (g)-(k), 80 % (l), 70 % (m)-(q), 60 % (r), 50 % (s)); (a)-(k) and (m)-(q) are transcribed
here. Parts (l), (r), (s) (pdf p43, p49, p50 for Table V; p62, p68, p69 for Table VI) are not
transcribed.

- Test procedure (pdf p7, printed 3): "For the 70, 90, and 100 percent of design speeds, data were
  recorded at five or more flows from maximum to near-stall conditions. For the 50, 60, and 80 percent
  of design speeds, data were recorded at the near-stall flow only. Data were taken at nine radial
  positions for each flow point."
- Peak efficiency at design speed (pdf p9, printed 5): "At design speed the rotor and stage achieved
  peak efficiencies of 0.872 and 0.845, respectively, at a mass flow of 20.82 kilograms per second.
  The rotor and stage pressure ratios at peak efficiency conditions were 1.875 and 1.842,
  respectively." This is reading 3978 (orifice airflow 20.82, rotor PR 1.875, stage PR 1.842, stage
  TR 1.225, rotor eff 0.872, stage eff 0.845, 99.6 % speed). Same page: "The mass flow at which peak
  efficiency occurred is about 3 percent higher than the design flow." "The maximum value of rotor
  efficiency of 0.905 occurred at 70 percent of design speed." (reading 3995) "At all three speed
  lines (70, 90, and 100 percent of design speeds), the peak efficiency occurred near the maximum mass
  flow. The stage stall margin, based on conditions at stall and peak efficiency, is very good. At
  design speed the stall margin is 21.8 percent."
- Near design / near stall (pdf p9, printed 5): radial distributions are shown "for design speed at
  three flow conditions, maximum near design, and near stall" and "For the near-design flow
  conditions (20.1 kg/sec)". The text names no reading numbers. By flow: maximum = 4004 (orifice
  20.95), near design (20.1 kg/sec) = 3974 (orifice 20.13), lowest flow at design speed (near stall)
  = 3976 (orifice 18.20; highest rotor PR 2.036 and TR 1.277). This mapping is inferred from the
  flows, not stated. No near-choke point is named; 4004 is the maximum-flow point.
- Stall margin (eq. B23, pdf p19) evaluated from Table IV with 3978 as reference and 3976 as stall
  gives about 19.4 % (orifice flow) or 20.1 % (rotor-inlet flow), not the 21.8 % of the text; the
  stall point used for the margin is apparently not one of the tabulated readings. Not resolved.

### Measurement stations

- Station 1 upstream of the rotor, station 3 downstream of the stator, no measurement between the
  rows (pdf p7). Station 2 (rotor exit) values are derived (pdf p8, printed 4): "At each radial
  position total pressure and total temperature were translated along design streamlines from
  station 3. The mass-averaged total temperature was used as the total temperature for station 2.
  The arithmetic mean of the three highest total-pressure values from the circumferential
  distribution at station 3 was used as the total pressure at station 2. The radial distributions of
  static pressure and flow angle were calculated based on continuity of mass flow and radial
  equilibrium. Measured mass flow, rotative speed, design values of streamline geometry, and annulus
  wall blockages were specified."
- Axial positions of the stations are not given in the text; Fig. 1 shows them only as drawn (see
  "Flow path" above: the TP-1338 coordinate box carries no survey-plane marks).
- Tables V and VI are "at blade edges": RADII IN/OUT are the blade-edge radii of the nine streamlines,
  printed identically in all six readings (they differ from Table II rows 1-9 in the third decimal,
  e.g. rotor RP 1 IN 24.915 here vs 24.916 in Table II). Only RP 1-9 (5-95 % span) are printed; there
  are no TIP/HUB rows.
- No tip clearance and no stator configuration (shrouded/cantilevered, hub gap) is stated anywhere in
  TP-1338 (text search and the rendered pages read); scalars.json is unchanged.

### Averaging and efficiency definitions (Appendix B, pdf p16-19, printed 12-15)

- Circumferential averaging at station 3 (pdf p8, printed 4): "The nine values of total temperature
  were mass averaged to obtain the circumferentially averaged stator-outlet total temperature. The
  nine values of total pressure were divided by the rotor-inlet total pressure and converted to
  corresponding isentropic temperature ratios. These ratios were mass averaged, and the resulting
  value converted (through the isentropic-temperature-ratio pressure-ratio relation) to an average
  total pressure ratio." Radial averaging for the overall performance: "To obtain the overall
  performance, the radial distributions of the circumferentially averaged total temperature and total
  pressure were averaged using a procedure similar to that used for averaging the circumferential
  distributions of these parameters."
- Rotor total pressure ratio (B10) and stage total pressure ratio (B11): mass-weighted average of
  (P/P1)^((gamma-1)/gamma) (weights rho*Vz*r dr; discrete sum over NR radial elements of
  rho_i Vz_i dA_i), raised to gamma/(gamma-1), i.e. a mass-averaged isentropic temperature ratio
  (energy average). Rotor uses station 2, stage uses station 3.
- Total temperature ratio (B12): mass-weighted average of T2/T1 (station 2).
- Rotor adiabatic efficiency (B13): ((P2/P1)bar^((gamma-1)/gamma) - 1)/((T2/T1)bar - 1). Stage
  adiabatic efficiency (B14): ((P3/P1)bar^((gamma-1)/gamma) - 1)/((T2/T1)bar - 1), i.e. with the
  station-2 temperature ratio. Rotor-inlet mass-average temperature (B15).
- Momentum-rise efficiency (B16): ((P2/P1)bar^((gamma-1)/gamma) - 1) divided by the mass-weighted
  [(U V_theta)2 - (U V_theta)1]/(T1bar cp). Head rise coefficient (B17):
  (cp T1bar/Ut^2) [(P2/P1)bar^((gamma-1)/gamma) - 1]. Flow coefficient (B22): (Vz/Ut) at the LE.
  Airflow per unit annulus / frontal area (B20, B21): equivalent mass flow W sqrt(theta)/delta
  divided by A_an or A_f. Stall margin (B23).
- Blade-element EFF (B9): adiabatic (temperature-rise) efficiency from P_TE/P_LE and T_TE/T_LE.
  Stator EFF is printed 0.000 in Table VI.
- Data were "corrected to standard-day conditions based on the rotor-inlet condition" (pdf p8). The
  ratio 'Airflow per unit frontal area' / 'per unit annulus area' is 0.5322-0.5323 for every reading
  (consistent); these columns are equivalent flows and do not equal the orifice airflow divided by the
  Appendix A areas.

### Checks (a check never overrode a clear print)

- Table IV, all 19 readings: stage PR = rotor PR x stator PR within 0.0015; stage TR = rotor TR x
  stator TR within 0.0015; (PR^(0.4/1.4) - 1)/(TR - 1) matches the printed rotor and stage adiabatic
  efficiencies within 0.006 (largest differences at 70 % speed, reading 3995: rotor 0.911 vs 0.905,
  stage 0.855 vs 0.860, where PR and TR are small and print rounding dominates); percent speed =
  rpm/17188.7 within 0.05. No cell failed.
- Table V (six readings, RP 1-9): W = sqrt(VM^2 + (U - Vtheta)^2) and V = sqrt(VM^2 + Vtheta^2)
  within 0.15 m/s; ABS/REL BETAM = atan(Vtheta/VM), atan((U - Vtheta)/VM) within 0.1 deg; ABS
  MACH/MERID MACH = V/VM and REL MACH = ABS MACH x W/V within print rounding; MERID VEL R = VM out/VM
  in within 0.0015; EFF = (PR^0.2857 - 1)/(TR - 1) within 0.006; INCIDENCE MEAN - SS, REL BETAM OUT -
  DEV and REL BETAM IN - INCIDENCE MEAN constant across the six readings at each RP within 0.1 deg
  (fixed blade angles); solidity implied by D FACT and by LOSS PARAM/LOSS COEFF consistent across
  readings; PROF/TOT ratios of LOSS PARAM and LOSS COEFF agree. All passed. U/r is constant only to
  about 0.8 % within readings 4004, 3977 and 3974 (0.1-0.2 % in the others); this is in the printed
  wheel speeds of whole rows, not a single glyph, and is left as printed.
- Table VI (six readings): U = 0, REL = ABS for angles, velocities and Mach numbers, TOTAL TEMP RATIO
  1.000 everywhere; V, angle and Mach relations as above; total-loss coefficient
  (1 - PR)/(1 - (1 + 0.2 M1^2)^-3.5) agrees with LOSS COEFF TOT within 0.004 in every row. All passed
  except the print error listed below.

### Reading notes and print defects (Tables IV-VI)

- TP1338_tableVI_stator35_reading3974.csv, RP 9, REL BETAM IN: printed '15.4' clearly (300, 400 and
  600 dpi). ABS BETAM IN of the same row is 45.4 and for a stator REL = ABS, so the print is wrong
  (should be 45.4). Kept as printed, without '?' (print error, not a reading doubt).
- TP1338_tableV_rotor35_reading3977.csv, RP 1, TOTAL TEMP IN: last digit printed as a filled blob
  (0 or 8); transcribed '288.8?'. No exact relation fixes it (other readings print 288.5-288.9 at
  RP 1). It was the only '?' cell of the 100 percent parts; see the 90 and 70 percent subsection for the other.
- TP1338_tableV_rotor35_reading4004.csv, RADII IN rows 4-8 and RADII OUT row 4: digits partly broken
  in the print ('2?.162', '21.?25', '20.2?1', '19.0?0', '18.5?5'; '22.?771'); resolved without '?'
  because the blade-edge radii are printed identically and clearly in the other five readings
  (23.162, 21.725, 20.221, 19.020, 18.595; 22.771) and the legible digits agree.
- TP1338_tableV_rotor35_reading4004.csv, RP 4, LOSS COEFF PROF '-.002' and LOSS PARAM PROF '-.000':
  printed without the leading zero; kept as printed (other cells print '0.xxx').
- TP1338_tableVI_stator35_reading4004.csv, RP 5 LOSS COEFF TOT and RP 9 LOSS PARAM TOT: decimal point
  faint ('0 040', '0 031'); written 0.040 and 0.031 (the PROF columns of the same rows print 0.040 and
  0.031 and equal TOT throughout this table).
- Table IV labels: 'ROTCR HEAD-RISE COEFFICIENT' (100 % part) and 'ROTCR ADIABATIC EFFICIENCY' (50 %
  part) are printed with the typo C for O; kept as printed. Dot leaders dropped. The 'M' of the
  line-printer font looks like 'H' in all labels; written as M.

### Tables V-VI at 90 and 70 percent speed

Added from the same report: Table V parts (g)-(k) and (m)-(q) (pdf p38-42 and p44-48, printed 34-38
and 40-44) and Table VI parts (g)-(k) and (m)-(q) (pdf p57-61 and p63-67, printed 53-57 and 59-63).
Reading number confirmed in each part title. Rendered at 300 dpi; second full read from 400-dpi
crops, cell by cell, with the transcribed row printed under each image row; suspect cells at 600 dpi.

| Speed | Part | Reading | Rotor file | Stator file |
|---|---|---|---|---|
| 90 % | (g) | 3979 | `TP1338_tableV_rotor35_reading3979.csv` | `TP1338_tableVI_stator35_reading3979.csv` |
| 90 % | (h) | 3982 | `TP1338_tableV_rotor35_reading3982.csv` | `TP1338_tableVI_stator35_reading3982.csv` |
| 90 % | (i) | 3983 | `TP1338_tableV_rotor35_reading3983.csv` | `TP1338_tableVI_stator35_reading3983.csv` |
| 90 % | (j) | 3984 | `TP1338_tableV_rotor35_reading3984.csv` | `TP1338_tableVI_stator35_reading3984.csv` |
| 90 % | (k) | 3985 | `TP1338_tableV_rotor35_reading3985.csv` | `TP1338_tableVI_stator35_reading3985.csv` |
| 70 % | (m) | 3995 | `TP1338_tableV_rotor35_reading3995.csv` | `TP1338_tableVI_stator35_reading3995.csv` |
| 70 % | (n) | 3994 | `TP1338_tableV_rotor35_reading3994.csv` | `TP1338_tableVI_stator35_reading3994.csv` |
| 70 % | (o) | 3993 | `TP1338_tableV_rotor35_reading3993.csv` | `TP1338_tableVI_stator35_reading3993.csv` |
| 70 % | (p) | 3990 | `TP1338_tableV_rotor35_reading3990.csv` | `TP1338_tableVI_stator35_reading3990.csv` |
| 70 % | (q) | 3989 | `TP1338_tableV_rotor35_reading3989.csv` | `TP1338_tableVI_stator35_reading3989.csv` |

Checks (a check never overrode a clear print):

- Table V (10 readings, RP 1-9): W = sqrt(VM^2 + (U - Vtheta)^2) and V = sqrt(VM^2 + Vtheta^2)
  within 0.16 m/s; ABS/REL BETAM from atan(Vtheta/VM), atan((U - Vtheta)/VM) within 0.1 deg; MERID
  MACH = ABS MACH x VM/V within 0.0015 and REL MACH = ABS MACH x W/V within 0.002; MERID VEL R = VM
  out/VM in within 0.0015; EFF = (PR^0.2857 - 1)/(TR - 1) within print rounding of PR and TR (+-0.0015);
  U/r constant within each reading to 0.4 %; RADII IN/OUT and PERCENT SPAN identical to the
  100-percent parts; INCIDENCE MEAN - SS, REL BETAM IN - INCIDENCE MEAN and REL BETAM OUT - DEV constant
  across all 11 rotor readings checked (10 new + 3974) within 0.2 deg at every RP; solidity implied by
  D FACT and by LOSS COEFF/LOSS PARAM consistent across the 10 readings (within 2 % and 6 %); PROF/TOT
  ratios of LOSS PARAM and LOSS COEFF agree. All passed.
- Table VI (10 readings): U = 0, TOTAL TEMP RATIO 1.000 everywhere, REL = ABS (string-identical) for
  angles, velocities and Mach numbers; V, ABS BETAM and Mach relations as above; total-loss coefficient
  (1 - PR)/(1 - (1 + 0.2 M1^2)^-3.5) agrees with LOSS COEFF TOT within 0.004 in every row; the
  blade-angle and solidity checks as for the rotor. All passed except the print error below.

Reading notes:

- TP1338_tableV_rotor35_reading3989.csv, RP 9, PEAK SS MACH NO: last digit only partly printed (an
  upper diagonal stroke; 4 or 6); transcribed '1.244?'. No relation fixes it. This and '288.8?' in
  reading 3977 are now the only '?' cells in Tables IV-VI.
- TP1338_tableVI_stator35_reading3989.csv, RP 9, REL MACH NO IN: printed '0.586' clearly (400 and
  600 dpi) while ABS MACH NO IN of the same row is 0.588 and for a stator REL = ABS (REL VEL IN = ABS
  VEL IN = 204.1). Print error; kept as printed, without '?'.
- TP1338_tableVI_stator35_reading3994.csv, RP 8, TANG VEL IN: last digit broken ('108.?'); written
  108.9 without '?' because V = sqrt(VM^2 + Vtheta^2) = 212.5 and ABS BETAM IN 30.8 with VM 182.4 admit
  only 108.9.
- Broken or faint glyphs resolved without '?' because a clear duplicate cell in the same row fixes them
  (stator REL = ABS, or TOT = PROF): reading 3993 stator RP 1 ABS VEL OUT and RP 2 ABS VEL OUT (REL
  VEL OUT 146.6, 155.9), RP 3 TANG VEL IN 100.0 (V and angle relation), RP 1 D FACT 0.330 (middle 3
  broken; trend 0.330, 0.319, 0.288 and the D FACT solidity check); reading 3984 stator RP 6 ABS MACH
  NO IN 0.700 and RP 9 TOTAL TEMP RATIO 1.000; reading 3984 rotor RP 1 ABS VEL IN 148.0 (= MERID VEL
  IN, TANG VEL IN -0.3).
- TP1338_tableVI_stator35_reading3995.csv, RP 6, D FACT: printed '-.003' (no leading zero); kept as
  printed.
