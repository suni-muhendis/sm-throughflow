# NASA Stage 37 (Rotor 37 / Stator 37)

Sources: NASA TP-1659 (performance report, Tables I-III, Fig. 1), NASA TP-1337 (design report,
Tables I-II, Fig. 1) and, as a separate source, NASA TM-107310 (isolated Rotor 37, Table 1 and running
clearance). See source.json.

## Specific notes

- Blade counts 36 rotor / 46 stator. Rotor-stator spacing approximately 0.7 cm (TP-1659 p5 pdf).
- Tip clearance of the stage-37 test: not stated in TP-1659 or TP-1337.
- TM-107310 (rotor alone, stator removed; a different configuration from the stage test): touch probe
  0.330 mm, rub probes 0.320 mm average, plus 0.075 mm tip-radius variance, giving an estimated
  design-speed running clearance of 0.400 mm (0.016 in.), 0.5 % of span, 0.7 % of tip chord; 0.500 mm at
  80 % speed and 0.580 mm at 60 % speed (pdf p45-46). In scalars.json with prefix `R37_isolated_`.
- TM-107310 Table 1 tip speed 454.14 m/s vs TP-1659 Table I 454.136 (rounding only).

## Reading notes (cells marked '?' and print defects)

- TP1659 Table II(b) stator 37 (pdf p23): HUB TOTAL TEMP RATIO printed with the last two digits broken ('1.0:)') -> 1.000? (every other row reads 1.000; stator). Row 9 LOSS PARAM TOT .033 vs PROF .032 while LOSS COEFF TOT = PROF = .097: transcribed as printed.
- TP1659 Tables I, II(a), III(a), III(b): clean print, no uncertain cells.

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
- Blade-element data at blade edges (Tables V and VI) for the 90, 80, 70, 60 and 50 percent speed
  readings. Table IV (all speeds) and Tables V-VI at 100 percent speed are transcribed; see
  "Measured performance (Tables IV-VI)" below.

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
| TP1659_tableII_stator37.csv | 13 | TOTAL TEMP RATIO | `1.000?` | `1.000` | stator does no work: TOTAL TEMP RATIO 1.000 on every other row | 600-dpi read: 1.0 legible, last two glyphs broken (':)'); value 1.000 |

## Measured performance (Tables IV-VI)

Transcribed from NASA TP-1659: Table IV (overall performance, pdf p26-28, printed 24-26), all six
speed parts; Table V (rotor 37, pdf p29-33, printed 27-31) and Table VI (stator 37, pdf p48-52,
printed 46-50), the five 100-percent-speed parts only. Rendered at 300 dpi; second read at 400 dpi,
suspect cells at 600 dpi. Files: `TP1659_tableIV_overall_<NNN>pct.csv` (readings as columns),
`TP1659_tableV_rotor37_reading<N>.csv`, `TP1659_tableVI_stator37_reading<N>.csv`.

### Readings

| Speed | Table IV part | Readings (printed order) |
|---|---|---|
| 100 % | (a) | 4193, 4192, 4182, 4188, 4187 |
| 90 % | (b) | 4209, 4208, 4207, 4205, 4204 |
| 80 % | (c) | 4194 |
| 70 % | (d) | 4202, 4203, 4201, 4198, 4196, 4195 |
| 60 % | (e) | 4215 |
| 50 % | (f) | 4218 |

Tables V and VI print one part per reading, (a)-(s), in the same order as Table IV (100 % (a)-(e),
90 % (f)-(j), 80 % (k), 70 % (l)-(q), 60 % (r), 50 % (s)); only (a)-(e) are transcribed here. The
remaining parts are on pdf p34-47 (Table V) and p53-66 (Table VI), not transcribed.

- Test procedure (pdf p5, printed 3): "For the 70, 90, and 100 percent of design speed, data were
  recorded at five or more flows from maximum to near-stall conditions. For the 50, 60, and 80 percent
  of design speeds, data were recorded at the near-stall flow only. Data were taken at nine radial
  positions for each flow point."
- Peak efficiency at design speed (pdf p7, printed 5): "At design speed the rotor and stage achieved
  peak efficiencies of 0.876 and 0.840, respectively, at an airflow of 20.74 kg/sec. The respective
  design efficiencies were 0.877 and 0.846. The rotor and stage pressure ratios at peak efficiency
  conditions were 2.056 and 2.000, respectively. The design rotor and stage pressure ratios were 2.106
  and 2.05, respectively. The airflow at which peak efficiency occurred is about 3 percent higher than
  the design flow." This is reading 4182 (orifice airflow 20.74, rotor-inlet 20.70, rotor PR 2.056,
  stage PR 2.000, stage TR 1.261, rotor eff 0.876, stage eff 0.840, 100.4 % speed). pdf p8 (printed
  6): "The maximum value of rotor efficiency of 0.93 occurred at 70 percent of design speed." (reading
  4203, 0.932) "At all three speed lines (70, 90, and 100 percent of design speeds speeds), the peak
  efficiency occurred near the maximum flow."
- Maximum / peak efficiency / near stall (pdf p8, printed 6): radial distributions are shown "for
  design speed at three flow conditions: maximum, peak efficiency, and near stall", with "For the peak
  efficiency flow condition (20.7 kg/sec)" and "At the near stall condition (19.6 kg/sec)". The text
  names no reading numbers. By flow: maximum = 4193 (orifice 20.93), peak efficiency = 4182 (20.74),
  near stall = 4187 (orifice 19.60; lowest flow and highest rotor PR 2.196 and TR 1.296 at design
  speed). This mapping is inferred from the flows, not stated. The text names no near-design point;
  pdf p7-8 only says "At the design flow rate rotor and stage pressure ratios exceeded the design
  value, and the efficiencies were slightly lower than design". The tabulated reading nearest the
  design flow of 20.2 kg/sec is 4188 (orifice 20.43); this is inferred, not stated.
- Stall margin (pdf p8, printed 6): "The stage stall margin, based on conditions at stall and peak
  efficiency, is only 10 percent at design speed. However, at 90 percent speed the stall margin is 20
  percent." Abstract (pdf p3): "The stage achieved a stall margin of 10 percent at design speed."
  Definition, eq. (B24) (pdf p18, printed 16): SM = [((P3/P1)stall (W sqrt(theta)/delta)ref) /
  ((P3/P1)ref (W sqrt(theta)/delta)stall) - 1] x 100. Stall point (pdf p7, printed 5): "The flow
  obtained just before stall occurred is call ed the stall flow. The pressure ratio at stall was
  obtained by extrapolating the total pressure obtained from the survey data to the stall flow." So
  the stall point is not a tabulated reading. Evaluated from Table IV with 4182 as reference and 4187
  as stall, (B24) gives 10.7 % (orifice or rotor-inlet flow); at 90 % speed with 4208 (stage peak
  efficiency 0.893) and 4204, 18.9 % (text: 20).

### Measurement stations

- Station 1 upstream of the rotor, station 3 downstream of the stator, no measurement between the
  rows (pdf p5, printed 3): "Because of the close spacing between the rotor and stator (approximately
  0.7 cm), no measurements were made between them." Station 2 (pdf p7, printed 5): "At each radial
  position total pressure and total temperature were translated along design streamlines from station
  3. The mass-averaged total temperature was used as the total temperature for station 2. The
  arithmetic mean of the three highest total-pressure values from the circumferential distribution at
  station 3 was used as the total pressure at station 2. The radial distributions of static pressure
  and flow angle were calculated based on continuity of mass flow and radial equilibrium. Measured
  airflow, rotative speed, design values of streamline geometry, and annulus wall blockages were
  specified." Blade edges (same page): "The data, measured at the three measuring stations, were
  translated to the blade leading and trailing edges by the method presented in reference 4."
- Axial positions are not given in the text; the Fig. 1 coordinate box marks "Survey planes" at outer
  -2.568, 4.445 and 10.640 cm (see "Flow path" above).
- Tables V and VI are "at blade edges": RADII IN/OUT are the blade-edge radii of the nine streamlines,
  printed identically in all five readings of each table (they differ from Table II rows 1-9 by up to
  0.002 in the third decimal, e.g. rotor RP 3 OUT 23.640 here vs 23.641 in Table II). Only RP 1-9
  (5-95 % span) are printed; there are no TIP/HUB rows.
- No tip clearance and no stator configuration (shrouded/cantilevered, hub gap) is stated anywhere in
  TP-1659 (text search and the rendered pages read; "gap" occurs only as the circumferential stator
  gap traversed at station 3); scalars.json is unchanged.

### Averaging and efficiency definitions (Appendix B, pdf p13-18, printed 11-16)

- Circumferential averaging at station 3 (pdf p6, printed 4): "The nine values of total temperature
  were mass averaged to obtain the circumferentially averaged stator-outlet total temperature. The
  nine values of total pressure were divided by the rotor-inlet total pressure and converted to
  corresponding isentropic temperature ratios. These ratios were mass averaged, and the resulting
  value converted through the isentropic-temperature-ratio - pressure-ratio relation) to an average
  total-pressure ratio." (sic, no opening parenthesis) Radial averaging (pdf p6-7): "To obtain the overall performance, the radial
  distributions of the circumferentially averaged total temperature and total pressure were averaged
  by using a procedure similar to that used for averaging the circumferential distributions of these
  parameters."
- Rotor total pressure ratio (B10) and stage total pressure ratio (B11): mass-weighted average of
  (P/P1)^((gamma-1)/gamma) (weights rho*Vz*r dr; discrete sum of rho_i Vz_i dA_i), raised to
  gamma/(gamma-1). Rotor uses station 2, stage uses station 3.
- Rotor total temperature ratio (B12): mass-weighted T2/T1. Stage total temperature ratio (B14):
  mass-weighted T3/T1 (station 3).
- Rotor adiabatic efficiency (B13): ((P2/P1)bar^((gamma-1)/gamma) - 1)/((T2/T1)bar - 1). Stage
  adiabatic efficiency (B15): ((P3/P1)bar^((gamma-1)/gamma) - 1)/((T3/T1)bar - 1), i.e. with the
  stage (station-3) temperature ratio. Rotor-inlet mass-averaged temperature (B16).
- Momentum-rise efficiency (B17): ((P2/P1)bar^((gamma-1)/gamma) - 1) divided by the mass-weighted
  [(U V_theta)2 - (U V_theta)1]/(T1bar cp). Head rise coefficient (B18): (cp T1bar/Ut^2)
  [(P2/P1)bar^((gamma-1)/gamma) - 1]. Equivalent airflow (B19) W sqrt(theta)/delta; equivalent speed
  (B20); airflow per unit annulus / frontal area (B21, B22) = equivalent airflow / A_an or A_f; flow
  coefficient (B23) (Vz/Ut) at the LE; stall margin (B24); rotor and stage polytropic efficiency (B25,
  B26).
- Blade-element EFF (B9): adiabatic (temperature-rise) efficiency from P_TE/P_LE and T_TE/T_LE;
  profile-loss parameter (B8) omega_p cos(beta'_m)TE/(2 sigma). Stator EFF is printed 0.000 in Table VI.
- Data correction (pdf p6, printed 4): "Orifice airflow, rotative speed, total pressures, static
  pressures, and temperatures were all corrected to standard-day conditions based on the rotor-inlet
  condition." The ratio 'Airflow per unit frontal area' / 'per unit annulus area' is 0.5033-0.5034
  for every reading (consistent).

### Checks (a check never overrode a clear print)

- Table IV, all 19 readings: stage PR = rotor PR x stator PR within 0.0017; stage TR = rotor TR x
  stator TR exactly (stator TR 1.000 everywhere); (PR^(0.4/1.4) - 1)/(TR - 1) matches the printed
  rotor and stage adiabatic efficiencies within 0.005 (largest: 50 % reading 4218 rotor 0.843 vs
  0.848; 70 % reading 4202 stage 0.830 vs 0.826; small PR and TR, print rounding dominates); percent
  speed = rpm/17188.7 within 0.05. No cell failed (after the two glyph resolutions listed below).
- Table V (five readings, RP 1-9): W = sqrt(VM^2 + (U - Vtheta)^2) and V = sqrt(VM^2 + Vtheta^2)
  within 0.15 m/s; ABS/REL BETAM = atan(Vtheta/VM), atan((U - Vtheta)/VM) within 0.1 deg; MERID MACH =
  ABS MACH x VM/V within 0.0015; REL MACH = ABS MACH x W/V within 0.0015 except three cells within
  0.0018 (4182 RP 3 IN 1.477, 4188 RP 5 IN 1.386, 4187 RP 2 IN 1.448; clear prints, inside the combined
  rounding of M, V and W); MERID VEL R = VM out/VM in within 0.0015; EFF = (PR^0.2857 - 1)/(TR - 1)
  within 0.006; INCIDENCE MEAN - SS, REL BETAM IN - INCIDENCE MEAN and REL BETAM OUT - DEV constant
  across the five readings at each RP within 0.1 deg (fixed blade angles); rotor-exit total
  temperature (TOTAL TEMP IN x TOTAL TEMP RATIO) equals Table VI TOTAL TEMP IN of the same reading and
  RP within 0.17 K in all 45 rows. All passed. U/r is constant within 0.2 % in readings 4193, 4192,
  4188 and 4187 but rises from 18.00 (RP 1) to 18.13 (RP 9) in reading 4182 (0.7 %); this is in the
  printed wheel speeds of whole rows, not a single glyph, and is left as printed.
- Table VI (five readings): U = 0, REL = ABS for angles, velocities and Mach numbers, TOTAL TEMP RATIO
  1.000 everywhere; V, angle and Mach relations as above; total-loss coefficient
  (1 - PR)/(1 - (1 + 0.2 M1^2)^-3.5) agrees with LOSS COEFF TOT within 0.004 in every row;
  INCIDENCE MEAN - SS, REL BETAM IN - INCIDENCE MEAN and REL BETAM OUT - DEV constant across readings
  within 0.1 deg. All passed.

### Reading notes and print defects (Tables IV-VI)

No cell carries '?'. Every uncertain glyph below was resolved by an exact relation or a clear second
reading; none overrides a clear print.

- TP1659_tableIV_overall_090pct.csv, reading 4205, ROTOR ADIABATIC EFFICIENCY: printed '8.879' (the
  leading 0 filled in, the same filled-zero glyph appears elsewhere); written 0.879. Check: PR 1.896,
  TR 1.228 give 0.880; momentum-rise efficiency 0.878.
- TP1659_tableIV_overall_090pct.csv, reading 4207, PERCENT OF DESIGN SPEED: printed '90.8' (filled
  zero); written 90.0. Check: 15468.0/17188.7 = 89.99 %.
- TP1659_tableIV_overall_070pct.csv, reading 4196, ROTATIVE SPEED: printed '12036.1.' with a stray
  trailing dot; written 12036.1.
- TP1659_tableIV_overall_100pct.csv: reading 4192 AIRFLOW AT ROTOR OUTLET first glyph oddly formed,
  read 20.84; reading 4187 ROTOR ADIABATIC EFFICIENCY printed with a stray mark ('0:852'), read 0.852
  (check 0.851).
- Table IV labels: 'ROTCR HEAD-RISE COEFFICIENT' (70 % part) printed with the typo C for O; kept as
  printed. 80 % part prints 'HEAD-RISE,COEFFICIENT' with a speck after RISE; written without it. Dot
  leaders dropped. The 'M' of the line-printer font looks like 'H' in all labels; written as M.
- TP1659_tableV_rotor37_reading4193.csv, TOTAL TEMP IN: RP 3 third glyph broken (8 or 9, closer to a
  9); written 288.3, because 288.3 x 1.213 = 349.7 equals Table VI reading 4193 RP 3 TOTAL TEMP IN
  349.7, while 289.3 would leave a 1.2 K mismatch (all other 44 rows agree within 0.17 K). RP 4 and
  RP 5 middle glyph broken ('2?8.3', '2?8.2'); written 288.3 and 288.2 (same check: 348.6 vs 348.6,
  350.2 vs 350.0).
- TP1659_tableV_rotor37_reading4193.csv, RP 9 TANG VEL IN: printed '-0.8' (filled zero); written
  -0.0 (ABS VEL IN = MERID VEL IN = 212.4, ABS BETAM IN -0.0).
- TP1659_tableV_rotor37_reading4192.csv, RP 8 LOSS COEFF PROF: middle digit faint ('0.?35'); written
  0.035 (PROF <= TOT 0.095; PROF/TOT agrees with LOSS PARAM 0.008/0.023).
- TP1659_tableV_rotor37_reading4182.csv, RP 2 TOTAL TEMP RATIO: second digit faint ('1.?74'); written
  1.274 (EFF 0.773 with PR 1.959 gives TR 1.274).
- TP1659_tableV_rotor37_reading4188.csv: RP 2 EFF decimal point faint ('0 765'), written 0.765; RP 9
  INCIDENCE SS '-1.5' with a broken 5 (MEAN - SS = 7.1 as at RP 9 in the other readings).
- TP1659_tableV_rotor37_reading4187.csv: RP 2 REL BETAM OUT broken ('5?.9') -> 55.9
  (atan((430.6 - 222.2)/141.1) = 55.90); RP 4 TOTAL PRESS RATIO ('2.1?8') -> 2.198 (EFF 0.828 and TR
  1.305 need PR 2.199; 2.188 would give 0.822); RP 3-5 TANG VEL IN printed '-0.0.', '-0 0', '0 (' ->
  -0.0, -0.0, 0.0 (V = VM in each row; no minus sign printed at RP 5); RP 6 WHEEL SPEED OUT last glyph
  small and raised ('368.?') -> 368.9 (U/r of RP 6 gives 368.88); RP 7 REL MACH NO OUT ('0.6?8') ->
  0.628 (0.808 x 226.5/291.5 = 0.6278); RP 8 LOSS PARAM TOT ('0.?28') -> 0.028; RP 9 D FACT ('0.6?2')
  -> 0.602 (Lieblein D with the solidity back-solved from readings 4188 and 4182 at RP 9, 1.734, gives
  0.6017).
- TP1659_tableVI_stator37_reading4192.csv: RP 1 REL VEL IN ('2?1.7') -> 241.7 (= ABS VEL IN); RP 2
  LOSS COEFF PROF ('? 095') -> 0.095 (= TOT, PROF = TOT in this reading); RP 9 D FACT ('0.?88') ->
  0.388 (D with the solidity back-solved from readings 4193 and 4182 at RP 9, 1.46, gives 0.3876).
- TP1659_tableVI_stator37_reading4188.csv: RP 9 of the fourth printed block (PERCENT SPAN, INCIDENCE
  MEAN/SS, DEV, D FACT, EFF, LOSS COEFF TOT/PROF, LOSS PARAM TOT/PROF) is not printed on the page (the
  block ends at RP 8; the pdftotext layer also has no such row); these ten cells are left empty. RP 1
  EFF printed 'G.000' -> 0.000; RP 2 D FACT printed '0..630' (stray dot) -> 0.630.
- TP1659_tableVI_stator37_reading4187.csv, RP 2 REL MACH NO OUT ('?.438') -> 0.438 (= ABS MACH NO OUT).
- TP1659_tableVI_stator37_reading4182.csv: RP 3 TOTAL TEMP IN and RP 6 MERID VEL OUT printed with a
  displaced decimal point ('363.5', '214.5' with the point low); read 363.5 and 214.5 (V relation
  holds).
