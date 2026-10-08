# Stage 18-13 and mods (NASA TM X-3472) transcription notes

Source: Lewis, Urasek, Reid, NASA TM X-3472 (February 1977), NTRS 19770010055,
file `TMX3472_192PR.pdf`: "Effects of Reset Stators and a Rotating, Grooved
Stator Hub on Performance of a 1.92-Pressure-Ratio Compressor Stage".
Rotor 18, stator 13 (pdf p4). The baseline stage was designed and first
tested in ref. 1 (Lewis, Reid, Tysl, NASA TM X-3100, 1974); it has since
been transcribed (files `TMX3100_*`, see the section "TM X-3100" at the
end): same blading, plus blade counts, clearance, profile type and damper.

## Configurations

- **Baseline (stage 18-13)**: geometry = Tables IV and V of this report
  ("The blade geometry for the original configuration is given in table IV
  ... and in table V", pdf p4).
- **Mod 1**: same rotor; stator blades reset 2 deg open. **No geometry table
  is printed for mod 1**; its stator geometry is the Table V geometry with
  the stagger changed by 2 deg "open" (direction relative to KIC/KOC/SETTING
  ANGLE not stated; interpretation left to the later step).
- **Mod 2**: mod 1 stators plus the stationary stator hub liner replaced by a
  rotating, circumferentially grooved hub extending from the rotor hub TE to
  the stator TE; grooves under the stator blades about 0.25 cm deep and
  0.25 cm wide, lands 0.76 cm wide (pdf p4, p10; Figure 4 photograph only).
  Number of grooves and their axial positions are not given.

All three configurations share the rotor and the flow path. Design tables
(I-V) are for the baseline design.

## Files

- `TMX3472_tableI_design_overall.csv` (pdf p20).
- `TMX3472_tableII_rotor18_part1..4.csv` (pdf p21).
- `TMX3472_tableIII_stator13_part1..4.csv` (pdf p22).
- `TMX3472_tableIV_rotor18_part1..3.csv`, `TMX3472_tableV_stator13_part1..3.csv`
  (pdf p23, printed rotated 90 deg; read from a 300-dpi render rotated
  upright).
- `TMX3472_fig2_flowpath_coordinates.csv` (Figure 2 inset, pdf p86): read
  from this page, identical in every value to the 14-10 / 12-5 / 8-8 inset.
  `↓` = printed down-arrow; FOOTNOTE `a` = instrumentation survey plane.

Tables print no units row (row 2 empty); units per appendix C. The print
quality of pdf p21-23 is poor (broken zeros that look like `C`, `:` or `3`).

## Uncertain cells ('?')

- Table II part2, RP 5, ABS VEL OUT: the glyph reads `257.4` at 400 dpi,
  but the velocity triangle (Vm 170.2, Vt 206.2) gives 267.4, and the
  neighbours are 265.5 / 269.3. Transcribed `257.4?`; probably a
  misprint or misread of 267.4.
- Table III part3, RP 3, PEAK SS MACH NO: last digit broken (`1.11C`).
  Transcribed `1.110?` (RP 2 is 1.110; RP 4 1.139).
- Table III part4, RP 11, LOSS PARAM PROF: last digit broken. Transcribed
  `0.040?` (pdftotext reads 0.043; PROF/TOT ratio from the loss coefficients
  gives about 0.041).

All other cells pass the consistency checks (U = omega r at 16100 rpm,
velocity triangles, Mach ratios, MERID VEL R, camber = KIC - KOC; solidity
with 56 rotor / 62 stator blades - counts derived, not printed).

## Inconsistencies noticed

- The Figure 2 flow-path inset is the same as the 14-10/12-5/8-8 inset
  (outer radius 25.273 at Z = 0, 24.511 at 4.572, 24.397 at 6.096, 24.384
  from 7.620 on), but the stage 18-13 design radii do not lie on it: rotor
  TIP RO = 24.359 at ZOC = 3.523 (casing there about 24.69 by linear
  interpolation), stator TIP RI = RO = 23.876 (casing 24.384), stator HUB
  RI 15.748 at ZIC 7.596 (hub 15.748 at Z = 7.620, consistent), stator HUB
  RO 16.510 at ZOC 11.407 (hub 16.510 at Z = 11.176, consistent). So the hub
  matches but the tip does not: the 18-13 casing contour is lower than the
  inset over the rotor exit and stator. The figure inset may have been
  reused from the earlier solidity-series reports. The true 18-13 flow path
  should be checked in TM X-3100 (ref. 1).
- Rotor TIP streamline slope OUT is +10.94 while RP 1 and 2 are -2.37 and
  -8.89 (as printed; clearly legible).
- Stator HUB CONE ANGLE 11.308 is smaller than RP 11 (11.508); as printed.
- Rotor 18 TOTAL CAMBER rises to 65.43 at the hub and KOC is negative from
  90 % span (hub -22.54): as printed.

## Text facts (scalars.json)

Design rotor PR 2.0 constant hub to tip, tip speed 422 m/s (Table I:
421.817), stage PR 1.925; stator about 3.0 cm downstream of the rotor TE;
stator hub inlet Mach 0.96 and D = 0.66; no part-span damper (none in text,
none in Figure 3(a) photograph); station 3 traverse one stator passage
5.8 deg; survey planes Z = -2.540, 6.096, 13.462 cm. Blade counts, tip
clearance and profile type are **not given** in this report.

## Conventions

beta from axial direction; K angles between mean camber line and meridional
plane; PERCENT SPAN from tip at rotor outlet; Z referenced from the rotor
blade hub leading edge (appendix A, Figure 2); ZIC..ZOC "axial distance ...
from inlet" (appendix C; rotor hub ZIC = 0.000). Stator hub ZIC 7.596 -
rotor hub ZOC 4.502 = 3.09 cm, consistent with "approximately 3.0 cm".

## Figure only

Figure 1 facility, Figure 3 photographs (rotor 18, stator 13), Figure 4
photograph of the grooved rotating hub, Figures 5-6 probes and layout.

## TM X-3100 (design report, ref. 1) - added 2026-10-08

Source: Lewis, Reid, Tysl, NASA TM X-3100 (E-7377), September 1974, NTRS
19740025108 (NTRS title has the typo "...compressor space"), file
`TMX3100_stage18_13_design.pdf` (92 pages). Confirmed as the design and
performance report of stage 18-13: "This report presents the aerodynamic
design and the performance of a single-stage fan designed for a pressure
ratio of 1.925 at a design tip speed of 422 meters per second ... designated
stage 18-13 (rotor 18, stator 13)" (pdf p4).

Files (pdf page = printed page + 2):
- `TMX3100_tableI_design_overall.csv` (pdf p21)
- `TMX3100_tableII_rotor18_part1..4.csv` (pdf p22)
- `TMX3100_tableIII_stator13_part1..4.csv` (pdf p23)
- `TMX3100_tableIV_rotor18_part1..3.csv` (pdf p24, printed upright)
- `TMX3100_tableV_stator13_part1..3.csv` (pdf p25, printed upright)
- `TMX3100_fig1_flowpath_coordinates.csv` (Figure 1 inset, pdf p64)
Figure only: Figure 2 facility, Figure 3 rotor 18 photo (pdf p65, a
mid-span damper ring is visible), Figure 4 stator 13 photo, probes and
layout figures.

### Same blading? Yes.

Tables I-V and the flow-path inset of TM X-3100 were compared cell by cell
with the TM X-3472 transcriptions: every number is the same. They are the
same computer output reprinted; TM X-3100 is the cleaner scan. So the
TM X-3472 baseline (and the mod 1/mod 2 rotor) is the TM X-3100 design.
Differences found are reading/print issues only:

- Rotor Table II part 2, RP 5 ABS VEL OUT: TM X-3100 prints `257.4`
  unambiguously (checked at 600 dpi). It is a misprint in the original
  program output (triangle gives 267.4), not a reading error. Transcribed
  without `?` in the TMX3100 file; the TMX3472 file keeps `257.4?`.
- Stator Table III part 1, TIP REL BETAM OUT: TM X-3100 prints `0.`;
  the TMX3472 file has `-0.` (a speck in front of the 0 in that print).
  The TMX3472 file was left unchanged; the true printed value is `0.`.
- Stator Table III part 4, RP 4 D-FACT: TM X-3100's last digit looks like a
  broken 6; TM X-3472 prints 0.488 clearly. Written `0.488?` in TMX3100.
- Still uncertain in both prints: stator RP 3 PEAK SS MACH NO `1.110?`, RP
  11 LOSS PARAM PROF `0.040?`, stator HUB CONE ANGLE 11.308 (looks like a
  3 in both prints).

### Flow path

The TM X-3100 Figure 1 inset is identical to the TM X-3472 Figure 2 inset.
So the casing/tip-radius mismatch noted above (rotor TIP RO 24.359 at ZOC
3.523 vs casing about 24.69; stator TIP 23.876 vs casing 24.384) is already
in the original design report and is not a reuse error of TM X-3472. The
inset is the only printed flow path; the true casing contour over the
rotor exit and stator remains unresolved (the blade-row tip radii in Tables
II-V may be the design streamline/blade tip, the inset the facility
annulus).

### Facts now known (scalars.json, keys `tmx3100_*`)

- 56 rotor blades (aspect ratio 2.6), 62 stator blades (aspect ratio 2.0),
  design tip solidity 1.7 both rows (pdf p5). Confirms the derived counts.
- Profile: multiple-circular-arc for rotor and stator; elements on conical
  surfaces, stacked on centers of gravity (pdf p4-5).
- Rotor tip clearance: nominal 0.05 cm, nonrotating, ambient (pdf p5).
  No running clearance given. No stator hub clearance (stator hubs seated
  on a rubber O-ring recessed in the inner casing; cantilever/shroud not
  otherwise described).
- **Part-span damper: yes.** "Each rotor blade has a vibration damper
  located at about a 52 percent span from the outlet rotor tip. The
  maximum thickness of the damper was 0.214 centimeter." (pdf p5). Damper
  losses were not included in the design (pdf p9). This corrects the
  earlier `part_span_damper: none mentioned` entry from TM X-3472 (left in
  place, not deleted); Figure 3 of TM X-3100 shows the damper ring. The
  dense survey rows at 47.5-57.5 % span bracket the damper.
- Rotor hub TE to stator hub LE axial spacing 3.1 cm (pdf p5); TM X-3472
  says "approximately 3.0"; Tables give 7.596 - 4.502 = 3.094.
- Design weight flow 29.5 kg/s (Table I 29.484), 202 kg/s/m2 annulus.
- Loss model: shock loss + profile loss from loss-D-factor correlations
  (rotor from TM X-2379, stator from CR-54621 MCA stator A) (pdf p4).
- Angle and table conventions are the same as TM X-3472 (Z from rotor
  blade hub LE; ZIC.. "from inlet"; PERCENT SPAN from tip at rotor outlet;
  K angles to the meridional plane).

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 4, still '?' 2, print errors 1.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TMX3100_tableIII_stator13_part3.csv | 6 | PEAK SS MACH NO | `1.110?` | `1.110?` | no independent relation; TM X-3472 print shows the same broken glyph | 600-dpi zoom (both prints): 1.11 plus a broken last glyph identical to RP 2's (C/J-like, which in these prints can be a 0, 3 or 9); still uncertain, kept |
| TMX3100_tableIII_stator13_part4.csv | 7 | D-FACT | `0.488?` | `0.488` | TM X-3472 prints 0.488 clearly (same program output); Lieblein D = 1 - 197.6/289.0 + 19.979 x 201.5/(40.241 x 2.017 x 289.0) = 0.4879 | 600-dpi zoom: last glyph looks like a 6 (an 8 with the upper-right stroke dropped out); other print and relation give 0.488 |
| TMX3100_tableIII_stator13_part4.csv | 14 | LOSS PARAM PROF | `0.040?` | `0.040` | LOSS PARAM PROF = LOSS COEFF PROF cos(REL BETAM OUT)/(2 sigma) = 0.202 x cos 0/(2 x 2.497) = 0.0405; the same relation gives TOT 0.044 and HUB PROF 0.051 as printed; 0.043 excluded | 600-dpi zoom (both prints): last glyph is the J/C-shaped broken 0 typical of these prints; relation fixes 0.040 |
| TMX3472_tableIII_stator13_part3.csv | 6 | PEAK SS MACH NO | `1.110?` | `1.110?` | no independent relation; TM X-3100 print shows the same broken glyph | 600-dpi zoom (both prints): last glyph broken (C/J-like); still uncertain, kept |
| TMX3472_tableIII_stator13_part4.csv | 14 | LOSS PARAM PROF | `0.040?` | `0.040` | LOSS PARAM PROF = 0.202/(2 x 2.497) = 0.0405 (relation reproduces TOT 0.044 and HUB 0.051); 0.043 excluded | 600-dpi zoom (both prints): J-shaped broken 0; relation fixes 0.040 |
| TMX3472_tableII_rotor18_part2.csv | 8 | ABS VEL OUT | `257.4?` | `257.4` | velocity triangle sqrt(VM^2 + VTH^2) = sqrt(170.2^2 + 206.2^2) = 267.4 (neighbours 265.5 / 269.3); TM X-3100 prints 257.4 too | PRINT ERROR: 600-dpi read shows 257.4 clearly in both prints; the printed value is kept without '?' and disagrees with the triangle (267.4) |

Print errors / print disagreements found in this pass:

- TMX3472_tableII_rotor18_part2.csv row 8 ABS VEL OUT: printed `257.4`; velocity triangle sqrt(VM^2 + VTH^2) = sqrt(170.2^2 + 206.2^2) = 267.4 (neighbours 265.5 / 269.3); TM X-3100 prints 257.4 too.
