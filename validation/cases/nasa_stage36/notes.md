# NASA Stage 36 (Rotor 36 / Stator 36)

Sources: NASA TP-1974 (performance report, Tables I-VI, Fig. 1) and NASA TP-1337 (design report,
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
- TP-1974 Tables V and VI (blade-element data at blade edges) for the readings below 100 percent of
  design speed, parts (a)-(n) (pdf p21-34 and p40-53). Table IV (all speeds) and the 100-percent parts
  of Tables V and VI are transcribed; see "Measured performance (Tables IV-VI)" below.

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

## Measured performance (Tables IV-VI)

Transcribed from NASA TP-1974: Table IV (overall performance, pdf p18-20, printed 15-17), all six
speed parts; Table V (rotor 36, pdf p35-39, printed 32-36) and Table VI (stator 36, pdf p54-58,
printed 51-55), the five 100-percent-speed parts only. Rendered at 600 dpi; second read from fresh
crops of the same renders, cell by cell; suspect cells zoomed further. Files:
`TP1974_tableIV_overall_<NNN>pct.csv` (readings as columns), `TP1974_tableV_rotor36_reading<N>.csv`,
`TP1974_tableVI_stator36_reading<N>.csv`. Table numbering is the same as in TP-1338 (IV overall,
V rotor, VI stator); the blade-element table titles carry the suffix "-SI UNITS".

### Readings

| Speed | Table IV part | Readings (printed order) |
|---|---|---|
| 100 % | (a) | 4273, 4272, 4271, 4270, 4269 |
| 90 % | (b) | 4281, 4280, 4279, 4282, 4284, 4277 |
| 80 % | (c) | 4294 |
| 70 % | (d) | 4301, 4299, 4298, 4297, 4296 |
| 60 % | (e) | 4304 |
| 50 % | (f) | 4309 |

Tables V and VI print one part per reading, (a)-(s), from low to high speed and, within a speed, by
reading number: 50 % (a) 4309; 60 % (b) 4304; 70 % (c)-(g) 4296, 4297, 4298, 4299, 4301; 80 % (h)
4294; 90 % (i)-(n) 4277, 4279, 4280, 4281, 4282, 4284; 100 % (o)-(s) 4269, 4270, 4271, 4272, 4273.
This is the reverse of the Table IV column order at 100 % speed. Only (o)-(s) are transcribed; the
remaining parts are on pdf p21-34 (Table V) and p40-53 (Table VI).

- Test procedure (pdf p5, printed 2): "For 70, 90, and 100 percent of design speed, data were
  recorded at five or more flows from maximum to near-stall conditions. For 50, 60, and 80 percent of
  design speed, data were recorded at the near-stall flow only. Data were taken at nine radial
  positions for each flow point."
- Peak efficiency at design speed (pdf p6, printed 3): "At design speed the rotor and the stage
  achieved peak efficiencies of 0.852 and 0.821, respectively. The rotor peak efficiency occurred at
  the maximum flow (20.94 kg/sec) and a pressure ratio of 1.766. The stage peak efficiency occurred at
  a flow rate of 20.83 kilograms per second and a pressure ratio of 1.817. The design rotor and stage
  pressure ratios were 1.863 and 1.82, respectively. The flow at which rotor peak efficiency occurred
  was about 3 percent higher than design. The stage stalled at approximately the design flow but at a
  pressure ratio higher than the design value."
  - Stage peak efficiency = reading 4272 (orifice airflow 20.83, rotor PR 1.854, stage PR 1.817, stage
    TR 1.227, rotor eff 0.850, stage eff 0.821, 100.0 % speed). Reading 4271 also prints stage
    efficiency 0.821 (orifice 20.69, stage PR 1.852); the quoted flow and pressure ratio identify 4272.
  - Rotor peak efficiency = reading 4273 (maximum flow, orifice 20.94, rotor PR 1.766, rotor eff
    0.852; stage PR 1.730, stage eff 0.818).
- Near design / near stall (pdf p6, printed 3): radial distributions are shown "for design speed at
  three flow conditions: maximum, peak efficiency, and near stall"; "For the stage peak efficiency
  condition (20.8 kg/sec)". The text names no reading numbers. By flow: maximum = 4273, peak
  efficiency = 4272, near stall = 4269 (lowest tabulated flow at design speed: orifice 20.26 kg/sec,
  rotor PR 1.924, stage PR 1.887, stage TR 1.244, stage eff 0.815, 99.7 % speed). This mapping is
  inferred from the flows, not stated. The text names no separate near-design point; design flow is
  20.2 kg/sec, and "The flow at the stall condition was approximately equal to the design flow"
  (pdf p6).
- Other peaks (pdf p6): "The peak rotor efficiencies at 70 and 90 percent of design speeds were 0.912
  and 0.892, respectively." (readings 4301 and 4281, the maximum-flow point of each speed line.)
- Stall margin, definition (B24, pdf p11, printed 8):
  SM = [ (P3/P1)bar_stall (W sqrt(theta)/delta)_ref / ( (P3/P1)bar_ref (W sqrt(theta)/delta)_stall ) - 1 ] x 100.
  Quoted values: "The stage exhibited reasonably good (27 percent) stall margin based on conditions at
  peak efficiency and stall at 70 percent of design speed, but only about 11 percent at design speed."
  (pdf p6); Summary (pdf p4): "The stage achieved a stall margin based on conditions at peak
  efficiency and stall of about 11 percent at design speed."; Summary of Results (pdf p7): "Stage
  stall margin was 11 percent at design speed."
  The stall point is not a tabulated reading (pdf p6): "The airflow obtained just before stall
  occurred is called the stall airflow. The pressure ratio at stall was obtained by extrapolating the
  total pressure obtained from the survey data to the stall airflow." B24 evaluated from Table IV with
  4272 as reference and 4269 as stall gives 6.8 % (orifice flow) or 7.0 % (rotor-inlet flow); at 70 %
  speed (4299 reference, 4296 lowest flow) 22.7 % / 23.3 %. Both are below the quoted 11 % and 27 %,
  consistent with a stall airflow below the lowest tabulated reading. Not resolved.

### Measurement stations

- Station 1 upstream of the rotor, station 3 downstream of the stator (pdf p5): "Because of the close
  spacing between the rotor and the stator (approx 0.7 cm), no measurements were made between them."
  Station 2 values are derived (pdf p6, printed 3): "At each radial position total pressure and total
  temperature were translated along design streamlines from station 3. The mass-averaged total
  temperature was used as the total temperature for station 2. The arithmetic mean of the three
  highest total-pressure values from the circumferential distribution at station 3 was used as the
  total pressure at station 2. The radial distributions of static pressure and flow angle were
  calculated on the basis of continuity of mass flow and radial equilibrium. Measured airflow,
  rotative speed, and design values of geometry and annulus wall blockage were specified."
- "The data at the three stations were translated to the blade leading and trailing edges by the
  method presented in reference 5." (pdf p6). Axial positions of the stations are not given in the
  text; the Fig. 1 coordinate box marks survey planes at -2.568 and 8.890 cm and a calculation plane
  at 4.445 cm (see "Flow path" above).
- Tables V and VI are "at blade edges": RADII IN/OUT are printed identically in all five 100 %
  readings and equal Table II rows 1-9 to within 0.001 cm (e.g. rotor RP 2 IN 24.635 here vs 24.636 in
  Table II; stator RP 1 OUT 23.879 vs 23.880). Only RP 1-9 (5-95 % span) are printed; no TIP/HUB rows.
- Tip clearance is already in scalars.json (pdf p4). The report does not state the stator
  configuration (shrouded or cantilevered) or a hub gap (text searched, pages read); scalars.json is
  unchanged. The rotor-stator axial spacing "approx 0.7 cm" (pdf p5) is recorded here only.

### Averaging and efficiency definitions (Appendix B, pdf p9-11, printed 6-8)

- Circumferential averaging at station 3 (pdf p5, printed 2): "The nine values of total temperature
  were mass averaged to obtain the circumferentially averaged stator-outlet total temperature. The
  nine values of total pressure were divided by the rotor-inlet total pressure and converted to
  corresponding isentropic temperature ratios. These ratios were mass averaged, and the resulting
  value was converted (through the isentropic-temperature-ratio-pressure-ratio relation) to an
  average total-pressure ratio." Radial (pdf p6): "To obtain the overall performance, the radial
  distributions of the circumferentially averaged total temperature and total pressure were averaged
  by using a procedure similar to that used for averaging the circumferential distributions of these
  parameters."
- Rotor total-pressure ratio (B10) and stage total-pressure ratio (B11): mass-weighted average of
  (P/P1)^((gamma-1)/gamma) (weights rho Vz r dr; discrete sum of rho_i Vz_i dA_i), raised to
  gamma/(gamma-1). Rotor uses station 2, stage uses station 3.
- Rotor total-temperature ratio (B12): mass average of T2/T1 at station 2. Stage total-temperature
  ratio (B14): mass average of T3/T1 at station 3.
- Rotor adiabatic efficiency (B13): ((P2/P1)bar^((gamma-1)/gamma) - 1)/((T2/T1)bar - 1). Stage
  adiabatic efficiency (B15): ((P3/P1)bar^((gamma-1)/gamma) - 1)/((T3/T1)bar - 1). Unlike TP-1338
  (stage efficiency over the station-2 temperature ratio), TP-1974 uses the station-3 temperature
  ratio and tabulates it as STAGE TOTAL TEMPERATURE RATIO.
- Rotor-inlet mass-averaged temperature (B16); momentum-rise efficiency (B17); head-rise coefficient
  (B18) (cp T1bar/Ut^2)[(P2/P1)bar^((gamma-1)/gamma) - 1]; equivalent airflow (B19) W sqrt(theta)/delta;
  equivalent speed (B20); airflow per unit annulus / frontal area (B21, B22); flow coefficient (B23)
  (Vz/Ut) at the LE; stall margin (B24); rotor and stage polytropic efficiency (B25, B26, defined but
  not tabulated); meridional velocity ratio (B27).
- Blade-element EFF (B9), "Adiabatic (temperature rise) efficiency", is printed with
  (P_LE/P_TE)^((gamma-1)/gamma) - 1 over T_TE/T_LE - 1; the pressure ratio is evidently inverted in
  print (tabulated EFF agrees with (P_TE/P_LE)^0.2857 - 1, see checks). Stator EFF is printed 0.000.
- Data "were all corrected to standard-day conditions based on the rotor inlet" (pdf p5). The ratio
  'Airflow per unit frontal area' / 'per unit annulus area' is 0.5057-0.5058 for every reading.

### Checks (a check never overrode a clear print)

- Table IV, all 19 readings: stage PR = rotor PR x stator PR within 0.0011; stage TR = rotor TR x
  stator TR within 0.0010; (PR^(0.4/1.4) - 1)/(TR - 1) matches the printed rotor efficiency within
  0.004 and the stage efficiency (stage TR, B15) within 0.003; percent speed = rpm/17188.7 x 100
  within 0.04. No cell failed.
- Table V (five readings, RP 1-9): W = sqrt(VM^2 + (U - Vtheta)^2) and V = sqrt(VM^2 + Vtheta^2)
  within 0.15 m/s; ABS/REL BETAM = atan(Vtheta/VM), atan((U - Vtheta)/VM) within 0.1 deg; MERID MACH
  = ABS MACH x VM/V and REL MACH = ABS MACH x W/V within 0.0015, except three REL MACH NO IN cells off
  by 0.002 (4269 RP 6, 4271 RP 1, 4273 RP 1; clear prints, rounding); MERID VEL R = VM out/VM in
  within 0.0015; EFF = (PR^0.2857 - 1)/(TR - 1) within 0.006; U/r constant within each reading to
  0.5 %; REL BETAM IN - INCIDENCE MEAN, INCIDENCE MEAN - INCIDENCE SS and REL BETAM OUT - DEV constant
  across the five readings at each RP within 0.1 deg (fixed blade angles).
- Table VI (five readings): U = 0; REL = ABS for angles, velocities and Mach numbers; TOTAL TEMP RATIO
  1.000 everywhere; V, angle and Mach relations as above; total-loss coefficient
  (1 - PR)/(1 - (1 + 0.2 M1^2)^-3.5) agrees with LOSS COEFF TOT within 0.004; PROF = TOT for both loss
  columns in every row; fixed-blade-angle differences constant within 0.1 deg.
- Rotor to stator: rotor TOTAL TEMP IN x TOTAL TEMP RATIO = stator TOTAL TEMP IN within 0.25 K and
  rotor TOTAL PRESS IN x TOTAL PRESS RATIO = stator TOTAL PRESS IN within 0.015 N/cm2, every RP of
  every 100 % reading.

### Reading notes and print defects (Tables IV-VI)

- No cell carries '?'.
- TP1974_tableIV_overall_100pct.csv, reading 4273, FLOW COEFFICIENT and AIRFLOW PER UNIT FRONTAL
  AREA: the second digit of both cells is the same smudged glyph (a 0 with a filled waist that could
  be read as 8). Written 0.404 and 104.23: the frontal/annulus ratio 0.5057-0.5058 of every other
  reading gives 206.09 x 0.5057 = 104.22, and 0.404 continues the speed-line trend (0.400 at 4272);
  184.23 and 0.484 are excluded.
- TP1974_tableVI_stator36_reading4271.csv, RP 6, TOTAL PRESS RATIO: middle digit partly broken (3 or
  8). Written 0.985: the total-loss relation with ABS MACH NO IN 0.756 gives 0.048 for 0.985 against
  the printed LOSS COEFF TOT 0.049 (0.935 would give about 0.21).
- TP1974_tableVI_stator36_reading4269.csv, RP 7, ABS MACH NO IN: decimal point faint ('0 759');
  written 0.759 (REL MACH NO IN of the same row prints 0.759).
- Signed zeros ('-0.0', '0.0') in ABS BETAM IN and TANG VEL IN of Table V and INCIDENCE SS of Table VI
  reading 4269 RP 3 are kept as printed.
- Table IV labels: dot leaders dropped; no label typos in this report.
