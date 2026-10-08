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
