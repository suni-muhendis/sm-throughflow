# NASA Stage 38 (Rotor 38 / Stator 38)

Sources: NASA TP-2001 (performance report, Tables I-III, Fig. 1) and NASA TP-1337 (design report,
Tables I-II, Fig. 1). See source.json.

## Specific notes

- Blade counts 48 rotor / 62 stator. Rotor-stator spacing approx. 0.7 cm (TP-2001 p4 pdf).
- Tip clearance: not stated in TP-2001 (rendered pdf p3-4 read) or TP-1337. Stage 36 (same rotor family,
  aspect ratio 1.63) states 0.071 cm cold / 0.018 cm running, but that is a different rotor.
- **TP-2001 Table II(b) stator 38 is incomplete in this PDF**: the scanned page image is cut off on the
  right, so TOTAL PRESS RATIO, WHEEL SPEED OUT, PEAK SS MACH NO and LOSS PARAM PROF are missing. Another
  scan (e.g. a printed copy) is needed to complete it.

## Reading notes (cells marked '?' and print defects)

- TP2001 Table II(a) rotor 38 (pdf p14): clean print; row 3 TOTAL PRESS IN printed '10'.14' with a stray tick -> 10.14.
- TP2001 Table II(b) stator 38 (pdf p15): THE SCANNED PAGE IS CROPPED ON THE RIGHT (the embedded 300-dpi scan itself ends there). Four columns are not visible and are NOT in the CSV: TOTAL PRESS RATIO, WHEEL SPEED OUT, PEAK SS MACH NO, LOSS PARAM PROF. Partly visible headings were completed from the identical layout of the other Table II blocks: 'TOTAL [PRESS] IN', 'WHEEL [SPEED] IN', 'MERID VEL R', 'LOSS P[ARAM] TOT'. For the stator, WHEEL SPEED OUT is .0 in every other report and LOSS PARAM PROF equals TOT whenever LOSS COEFF PROF equals TOT, but these were not transcribed (not printed visibly). Row 2 ABS BETAM IN printed '4:.2' (second digit broken) -> 48.2? (REL BETAM IN of the same row reads 48.2). Row 9 TANG VEL IN first digit faint -> 217.7. TIP TOTAL TEMP RATIO printed .997 and TIP LOSS COEFF .063 (vs .091 at row 1): as printed.
- TP2001 Table III(a) rotor 38 (pdf p16): TIP KOC printed '55,39' (comma for decimal point) -> 55.39.
- TP2001 Table III(b) stator 38 (pdf p17): clean print. ZMC is not monotonic toward the hub (5.186 at row 8, 5.182 at row 9, 5.177 at HUB): as printed. TIP CONE ANGLE -8.087 vs row 1 -4.998 (same pattern as stator 36).

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
- Blade-element data at blade edges (TP-2001 Tables V and VI) for the 90, 80, 70, 60 and 50 percent
  speed readings. Table IV (all speeds) and Tables V-VI at 100 percent speed are transcribed; see
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

## Search for the four missing stator 38 columns (2026-10-08)

Not found. TOTAL PRESS RATIO, WHEEL SPEED OUT, PEAK SS MACH NO and LOSS
PARAM PROF of TP-2001 Table II(b) remain untranscribed. What was tried:

- TP2001.pdf (NTRS 19820014395) pdf p15: `pdfimages -list` shows one
  embedded 1-bit CCITT scan at 300 dpi (2504 x 3187 px, the full page). The
  extracted raw image ends at the same place as the render: the last
  visible headings are cut through the letters ("MERID P", "VEL R M",
  "LOSS P") and there is blank paper to the right, with the page number
  "13" printed further right. So the table strip was already trimmed on the
  printed page (paste-up), not by the scanner or the PDF crop box
  (MediaBox = CropBox = full page). Rendering at higher dpi cannot recover
  anything (300 dpi is the native resolution). The rotor 38 page (pdf p14)
  is complete (ink extends about 100 px further right).
- pdftotext layer of p15 and the NTRS full-text (.txt) download: same
  OCR of the same cut image; nothing beyond the cut.
- Other copies: NTRS lists only one download for 19820014395 and no other
  NTRS record for TP-2001. The Polytechnique Montreal LAVA wiki copy
  (lava-wiki.meca.polymtl.ca/_media/public/modeles/rotor_38/rotor38.pdf)
  is byte-identical (same MD5) to the NTRS file. HathiTrust record
  011424457 and core.ac.uk work 24912755 could not be opened (Cloudflare
  403/challenge). The JAXA AIREX record found is for TP-1974 (stage 36) and
  carries metadata only. Since the cut is in the printed page, any other
  scan of the same printing would probably show the same loss.
- Other reports: TP-1337 (design report of stages 35-38) prints only
  Table I (overall), Table II (mechanical) and the Appendix C manufacturing
  coordinates; it has no design blade-element tables. NASA TM-79280
  (NTRS 19800002791, "Experimental study of low aspect ratio compressor
  blading", summary of stages 35-38) has only overall-performance summary
  tables. NTRS searches for "stator 38" / "rotor 38" found no other report.
- Not derived: WHEEL SPEED OUT is .0 for every stator in the sister
  reports and LOSS PARAM PROF equals TOT wherever LOSS COEFF PROF equals TOT
  (true for every stator 38 row), but these are inferences, not printed
  values, and were left out per the transcription guide. TOTAL PRESS RATIO
  and PEAK SS MACH NO cannot be inferred reliably from the printed columns.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 1, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP2001_tableII_stator38.csv | 5 | ABS BETAM IN | `48.2?` | `48.2` | stator (U = 0): ABS BETAM IN = REL BETAM IN = 48.2 | 600-dpi read: second digit broken (4:.2); exact relation fixes 48.2 |

## Measured performance (Tables IV-VI)

Transcribed from NASA TP-2001: Table IV (overall performance, pdf p18-20, printed 16-18), all six
speed parts; Table V (rotor 38, pdf p35-40, printed 33-38) and Table VI (stator 38, pdf p55-60,
printed 53-58), the six 100-percent-speed parts only. Rendered at 300 dpi; Table IV second read at
400 dpi, Tables V-VI second read from enlarged 300-dpi crops, suspect cells at 600 dpi. Files:
`TP2001_tableIV_overall_<NNN>pct.csv` (readings as columns), `TP2001_tableV_rotor38_reading<N>.csv`,
`TP2001_tableVI_stator38_reading<N>.csv`. Unlike Table II(b), the Table VI pages are complete (no
column cut off).

### Readings

| Speed | Table IV part | Readings (printed order) |
|---|---|---|
| 100 % | (a) | 4129, 4128, 4123, 4121, 4120, 4119 |
| 90 % | (b) | 4140, 4139, 4133, 4132, 4131 |
| 80 % | (c) | 4093 |
| 70 % | (d) | 4097, 4098, 4099, 4100, 4101, 4095 |
| 60 % | (e) | 4104 |
| 50 % | (f) | 4102 |

Table IV prints each speed from maximum to minimum flow. Tables V and VI print one part per reading,
(a)-(t), in a different order: by increasing speed and, within a speed, from minimum to maximum flow:
50 % (a) 4102; 60 % (b) 4104; 70 % (c)-(h) 4095, 4101, 4100, 4099, 4098, 4097; 80 % (i) 4093; 90 %
(j)-(n) 4131, 4132, 4133, 4139, 4140; 100 % (o)-(t) 4119, 4120, 4121, 4123, 4128, 4129. Only (o)-(t)
are transcribed here; (a)-(n) are on pdf p21-34 (Table V) and p41-54 (Table VI), not transcribed.
Table IV(e) is printed '(e) Percent of design speed' (the number is missing); it is the 60 % part
(speed order, PERCENT OF DESIGN SPEED 61.8, and Tables V/VI part (b) '60 Percent of design speed;
reading 4104').

- Test procedure (pdf p4, printed 2): "For 70, 90, and 100 percent of design speed, data were
  recorded at five or more flows from maximum to near-stall conditions. For 50, 60, and 80 percent of
  design speed, data were recorded at the near-stall flow only. Data were taken at nine radial
  positions for each flow point."
- Peak efficiency at design speed. Abstract (pdf p3): "At design speed the rotor achieved a peak
  efficiency of 0.849 at a pressure ratio of 1.969. The stage peak efficiency of 0.831 occurred at a
  pressure ratio of 1.944. For both the rotor and the stage, peak efficiency occurred at the minimum
  flow conditions, which were higher than the design flow." Results (pdf p5, printed 3): "At design
  speed the rotor and the stage achieved peak efficiencies of 0.849 and 0.831, respectively. For both
  the rotor and the stage the peak efficiency occurred near the minimum flow conditions. The rotor and
  stage pressure ratios at the peak efficiency conditions were 1.969 and 1.944, respectively. The
  design values of rotor and stage pressure ratio are 2.105 and 2.05. The stage stall point and peak
  efficiency point occurred at a flow slightly higher than the design value. The peak rotor
  efficiencies at 70 and 90 percent of design speed were 0.949 and 0.901, respectively." The pressure
  ratios identify reading 4120 (orifice airflow 20.67, rotor PR 1.969, rotor TR 1.252, rotor eff
  0.849; stage PR 1.944, stage TR 1.252, stage eff 0.831; 100.2 % speed). Reading 4119 (minimum flow)
  prints the same stage efficiency 0.831 (and rotor 0.848) at stage PR 1.977. The 70 and 90 % values
  are readings 4097 (0.949) and 4133 (0.901).
- Summary (pdf p6, printed 4): "1. At design speed the peak stage efficiency of 0.831 occurred near
  the stall flow of 20.4 kilograms per second. The pressure ratio was 1.944." This mixes the two
  readings: 20.4 kg/sec is the flow of 4119 (orifice 20.44), PR 1.944 is 4120 (orifice 20.67). Not
  resolved.
- Near stall / maximum flow (pdf p5, printed 3): radial distributions are shown "for design speed at
  three flow conditions: maximum, midflow, and near stall" and "For the near-stall flow of 20.4
  kilograms per second". Near stall at design speed = 4119 (orifice 20.44, lowest flow, highest rotor
  PR 2.004 and TR 1.259); the text gives the flow, not the reading number. Maximum flow = 4129
  (orifice 20.97); the stator text's "flow of 21.0 kilograms per second" is probably also 4129. The
  "midflow" reading is not identified. No near-design point is named: the design flow 20.2 kg/sec lies
  below the whole measured range at 100 % speed (pdf p5: "The stage stalled at a flow higher than
  design").
- Stall margin: defined by eq. (B24), pdf p10 (printed 8): SM = [ (P3/P1)stall (W sqrt(theta)/delta)ref
  / ((P3/P1)ref (W sqrt(theta)/delta)stall) - 1 ] x 100. TP-2001 states no stall-margin value. The
  stall point is not a tabulated reading (pdf p5): "The airflow obtained just before stall occurred is
  called the stall airflow. The pressure ratio at stall was obtained by extrapolating the total
  pressure obtained from the survey data to the stall airflow." For orientation only, B24 with 4120 as
  reference and 4119 as stall gives 2.8 % (orifice flow); this is not a printed value.

### Measurement stations

- Station 1 upstream of the rotor, station 3 downstream of the stator, no measurement between the
  rows (pdf p4: "Because of the close spacing between the rotor and the stator (approx. 0.7 cm), no
  measurements were made between them."). Station 2 (rotor exit) values are derived (pdf p5, printed
  3): "At each radial position total pressure and total temperature were translated along design
  streamlines from station 3. The mass-averaged total temperature was used as the total temperature
  for station 2. The arithmetic mean of the three highest total-pressure values from the
  circumferential distribution at station 3 was used as the total pressure at station 2. The radial
  distributions of static pressure and flow angle were caculated [sic] on the basis of continuity of
  mass flow and radial equilibrium. Measured airflow, rotative speed, design values of geometry, and
  annulus wall blockages were specified." and "The data, at the three stations, were translated to the
  blade leading and trailing edges by the method presented in reference 4."
- Axial positions: the text gives none; the Fig. 1 coordinate box marks inner -2.568 and 8.890 cm as
  "Instrumentation survey planes" (see "Flow path" above).
- Tables V and VI are "at blade edges": RADII IN/OUT are the blade-edge radii of the nine streamlines,
  printed identically in all six readings except two cells (see reading notes). Only RP 1-9 (5-95 %
  span) are printed; there are no TIP/HUB rows.
- No tip clearance and no stator configuration (shrouded/cantilevered, hub gap) is stated anywhere in
  TP-2001 (text search and the rendered text pages p3-6 read); scalars.json is unchanged.

### Averaging and efficiency definitions (Appendix B, pdf p8-10, printed 6-8)

- Circumferential averaging at station 3 (pdf p4, printed 2): "The nine values of total temperature
  were mass averaged to obtain the circumferentially averaged stator-outlet total temperature. The
  nine values of total pressure were divided by the rotor-inlet total pressure and converted to
  corresponding isentropic temperature ratios. These ratios were mass averaged, and the resulting
  value converted (through the isentropic-temperature-ratio-pressure-ratio relation) to an average
  total-pressure ratio." Radial averaging (pdf p4-5): "To obtain the overall performance, the radial
  distributions of the circumferentially averaged total temperature and total pressure were averaged
  by using a procedure similar to that used for averaging the circumferential distributions of these
  parameters."
- Rotor total-pressure ratio (B10) and stage total-pressure ratio (B11): mass-weighted average of
  (P/P1)^((gamma-1)/gamma) (weights rho Vz r dr; discrete sum over NR radial elements of rho_i Vz_i
  dA_i), raised to gamma/(gamma-1) (energy average). Rotor uses station 2, stage station 3.
- Rotor total-temperature ratio (B12): mass-weighted T2/T1. Stage total-temperature ratio (B14):
  mass-weighted T3/T1 (station 3).
- Rotor adiabatic efficiency (B13): ((P2/P1)bar^((gamma-1)/gamma) - 1)/((T2/T1)bar - 1). Stage
  adiabatic efficiency (B15): ((P3/P1)bar^((gamma-1)/gamma) - 1)/((T3/T1)bar - 1), i.e. with the
  station-3 temperature ratio (TP-1338 for stage 35 uses the station-2 ratio and numbers its
  equations differently).
- Rotor-inlet mass-averaged temperature (B16); momentum-rise efficiency (B17):
  ((P2/P1)bar^((gamma-1)/gamma) - 1) divided by the mass-weighted [(U V_theta)2 - (U V_theta)1]/(T1bar
  cp); head-rise coefficient (B18): (cp T1bar/Ut^2)[(P2/P1)bar^((gamma-1)/gamma) - 1]; equivalent
  airflow (B19) W sqrt(theta)/delta; airflow per unit annulus / frontal area (B21, B22); flow
  coefficient (B23): (Vz/Ut) at the LE; stall margin (B24); polytropic efficiencies (B25, B26);
  meridional velocity ratio (B27).
- Blade-element EFF (B9): adiabatic (temperature-rise) efficiency from P_TE/P_LE and T_TE/T_LE.
  Stator EFF is printed 0.000 in Table VI.
- Pdf p4: "Orifice airflow, rotative speed, total pressures, static pressures, and temperatures were
  all corrected to standard-day conditions based on the rotor inlet." The ratio 'Airflow per unit
  frontal area' / 'per unit annulus area' is 0.5054-0.5055 for every reading (consistent).

### Checks (a check never overrode a clear print)

- Table IV, all 20 readings: stage PR = rotor PR x stator PR within 0.0015; stage TR = rotor TR x
  stator TR within 0.0015; (PR^(0.4/1.4) - 1)/(TR - 1) matches the printed rotor and stage adiabatic
  efficiencies within 0.006 (largest differences at 70 % speed, readings 4097 stage 0.862 vs 0.857 and
  4099 stage 0.890 vs 0.895, where PR and TR are small and print rounding dominates); percent speed =
  rpm/17188.7 within 0.05. No cell failed.
- Table V (six readings, RP 1-9): W = sqrt(VM^2 + (U - Vtheta)^2) and V = sqrt(VM^2 + Vtheta^2)
  within 0.15 m/s; ABS/REL BETAM = atan(Vtheta/VM), atan((U - Vtheta)/VM) within 0.1 deg; MERID MACH =
  ABS MACH x VM/V and REL MACH = ABS MACH x W/V within 0.0015, except 4123 RP 2 REL MACH NO IN printed
  1.483 vs 1.4849 (clear print; rounding of the inputs); ABS MACH IN/OUT from V and static temperature
  (cp 1004.5, R 287.05) within 0.002; MERID VEL R = VM out/VM in within 0.0015; EFF = (PR^0.2857 -
  1)/(TR - 1) within 0.006; U/r constant within 1 %; INCIDENCE MEAN - SS, REL BETAM IN - INCIDENCE
  MEAN and REL BETAM OUT - DEV constant across the six readings at each RP within 0.1 deg (fixed blade
  angles); PROF/TOT ratios of LOSS PARAM and LOSS COEFF agree. All passed.
- Table VI (six readings): U = 0, REL = ABS for angles, velocities and Mach numbers, TOTAL TEMP RATIO
  1.000 and EFF 0.000 everywhere; V, ABS BETAM = atan(Vtheta/VM) and Mach relations as above;
  total-loss coefficient (1 - PR)/(1 - (1 + 0.2 M1^2)^-3.5) agrees with LOSS COEFF TOT within 0.006 in
  every row; fixed-blade-angle checks as above. All passed.

### Reading notes and print defects (Tables IV-VI)

No cell carries '?'. Cells resolved without '?':

- TP2001_tableIV_overall_100pct.csv, 4129 STATOR TOTAL PRESSURE RATIO: printed 'G.980' (leading 0
  broken) -> 0.980 (1.799 x 0.980 = 1.763 = printed stage PR).
- TP2001_tableIV_overall_070pct.csv: 4097 STATOR TOTAL TEMPERATURE RATIO last digit a slashed blob
  -> 1.000 (rotor TR 1.090 = stage TR 1.090; every other stator TR prints 1.000); 4095 ROTOR TOTAL
  PRESSURE RATIO last digit a slashed 0 -> 1.420 (1.420 x 0.993 = 1.410 = stage PR); 4101 ROTOR
  HEAD-RISE COEFFICIENT printed 'C.329' -> 0.329; 4100 PERCENT OF DESIGN SPEED printed '69 8'
  (decimal point missing) -> 69.8 (12002.6/17188.7 = 69.83 %).
- TP2001_tableV_rotor38_reading4121.csv, RP 1, DEV: second digit broken -> 10.2 (REL BETAM OUT - DEV =
  53.7 in all six readings at RP 1).
- TP2001_tableV_rotor38_reading4129.csv, RP 9, INCIDENCE SS: last digit broken ('-2.?') -> -2.2
  (INCIDENCE MEAN - SS = 7.2 in all six readings at RP 9).
- TP2001_tableVI_stator38_reading4119.csv, RP 5, RADII OUT: middle digit broken ('21.6?6') -> 21.676
  (printed clearly in the other five readings).
- TP2001_tableVI_stator38_reading4123.csv, RP 1 LOSS PARAM TOT '0.?59' -> 0.059 and RP 2 LOSS PARAM
  TOT '0.0?6' (the 4 looks like 1) -> 0.046: LOSS COEFF TOT = PROF in both rows, and the PROF loss
  parameters print 0.059 and 0.046.
- TP2001_tableVI_stator38_reading4128.csv, RP 7, REL MACH NO IN printed '^.809' -> 0.809 (= ABS MACH
  NO IN, stator).
- TP2001_tableVI_stator38_reading4129.csv, RP 9, MERID MACH NO IN printed 'C 619' -> 0.619 (0.845 x
  219.4/299.3 = 0.6194).
- Stray ticks and doubled dots (e.g. rotor 4121 RP 1 REL BETAM IN "69'.0", stator 4120 RP 4 TOTAL
  PRESS IN "19'.71") are print noise; the digits are clear.

Print discrepancies kept as printed (clear prints, not reading doubts):

- TP2001_tableV_rotor38_reading4129.csv, RP 7, RADII OUT: printed 19.492 (600 dpi); the other five
  readings print 19.482. U/r does not discriminate (351.1/19.492 = 18.013, 351.1/19.482 = 18.022;
  other rows 18.02-18.06).
- TP2001_tableVI_stator38_reading4121.csv, RP 8, RADII OUT: printed 19.538 clearly (600 dpi); the
  other five readings print 19.588.
- Table IV labels: dot leaders dropped; 'FLOW  COEFFICIENT' is printed with a double space (written
  with one). The 'M' of the line-printer font looks like 'H' in all labels; written as M.
