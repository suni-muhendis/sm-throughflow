# Stage 8E-8 tip-clearance series (NASA TP-2049) - transcription notes

Source: Moore, *Rotor Tip Clearance Effects on Overall and Blade-Element
Performance of Axial-Flow Transonic Fan Stage*, NASA TP-2049, September 1982,
NTRS 19820025513.

## Numbering
"stage 8E-8", "rotor 8E", "stator 8" (pdf p3, tables). The report says the
stage is "the same one that was described in detail in reference 5" = NASA
TM X-2926 (stage 8-8, sigma_tip 1.5, our catalogue file `TMX2926_sol15`). The
report does not explain the "E" suffix.

Cross-check against the independent transcription of TM X-2926 in
`../nasa_stage8_8/` (read only): Tables II, III, IV and V agree cell for cell
(1612 common cells), with the single exception of stator Table V row 2
DELTA INC (TM X-2926 prints 6.13; this report's print looks like 5.13, see
below). So the tabulated design and geometry of rotor 8E / stator 8 here are
identical to rotor 8 / stator 8 in TM X-2926, and both transcriptions are
confirmed.

## The four configurations
Same blading, casing insert machined to nominal nonrotating tip clearances of
0.061 (baseline), 0.102, 0.140, 0.178 cm. Larger clearances made by removing a
uniform increment from the insert over the rotor tips, faired back to the casing
about 1.3 cm upstream of the LE and downstream of the TE (Fig. 5, figure only).
Calculated wheel+blade growth plus eccentricity about 0.040 cm at design speed,
so running clearances are about 0.040 cm smaller (0.021, 0.062, 0.100, 0.138
cm, derived, not printed). Running clearance 0.2-1.2 % of LE blade height.
Data tables: VI(a)-(d) overall, VII (0.061), VIII (0.102), IX (0.140),
X (0.178); not transcribed here (measured data, not geometry).

The Fig. 2 flow-path box is the baseline casing; there is no coordinate table
for the recessed casing at larger clearances.

## Conventions
- Z from rotor blade hub leading edge (appendix A, Fig. 2 axis). Table
  columns ZIC/ZMC/ZTC/ZOC "axial distance from inlet hub to ..."; rotor HUB
  ZIC = 0.000, so same datum. Check: rotor HUB ZOC 4.295 to stator HUB ZIC
  7.628 = 3.333, matching the text 3.33 cm.
- Survey planes: Z = -2.540 (station 1), 6.096 (station 2), 13.462 (station 3).
- PERCENT SPAN from tip at rotor outlet; beta from axial; kappa to meridional
  plane; blade elements on cones (CONE ANGLE column).
- Profile type is not stated in this report. X FACTOR < 1 and distinct
  ZTC/KTC in both Tables IV and V indicate multiple-circular-arc sections for
  rotor and stator (stator X FACTOR 0.600 over the outer half).
- Rotor part-span damper at about 48 % span from the outlet tip (thickness
  0.214 cm): blade-element comparisons near 40-55 % span are suspect.
- Table II/IV rotor rows 4-8 are closely spaced around the damper (42.5, 45,
  47.5, 50, 52.5 % span); Table IV prints them rounded (43., 45., 48., 50., 53.).

## Cells marked '?'
- Table II row 5, PEAK SS MACH NO `1.513?` (middle digit damaged, "1.5:3").
- Table III row 5, PEAK SS MACH NO `1.012?` (damaged "1:0'2"; trend 1.008,
  ?, 1.017 supports 1.012).
- Table V row 2, DELTA INC `5.13?`: printed glyph looks like 5, but every
  other row is 5.86-6.14 and neighbours are 6.12 and 6.14; likely a damaged 6.
  TM X-2926 Table V prints 6.13 for the same cell.

## Inconsistencies noticed
- Fig. 2 inner radius at Z = 0 is 12.668 cm while Table II/IV rotor HUB RI is
  12.700 cm.
- Table III stator TIP TOTAL TEMP RATIO 1.001 (others 1.000), and HUB LOSS
  COEFF TOT 0.202 vs PROF 0.199 (others equal); as printed.
- Text design tip speed 423 m/s (the "423" is overstruck in the scan but
  legible); Table I gives 422.888.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 3, still '?' 0, print errors 1.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP2049_tableII_rotor8E.csv | 8 | PEAK SS MACH NO | `1.513?` | `1.513` | same blading printed in TM X-2926 Table II (rotor 8), row 5 PEAK SS MACH NO = 1.513 (all neighbouring cells identical in both prints) | 600-dpi read: 1.5 and final 3 clear, middle glyph damaged; other print gives 1.513 |
| TP2049_tableIII_stator8.csv | 8 | PEAK SS MACH NO | `1.012?` | `1.012` | same blading printed in TM X-2926 Table III (stator 8), row 5 = 1.012; trend 1.008, -, 1.017 | 600-dpi read: middle glyph damaged (1:012); other print gives 1.012 |
| TP2049_tableV_stator8.csv | 5 | DELTA INC | `5.13?` | `5.13` | TM X-2926 Table V prints 6.13 for the same cell; every other row is 5.86-6.14 (neighbours 6.12, 6.14) | PRINT ERROR: 600-dpi zoom shows a clear 5 (flat top bar, not a damaged 6); kept as printed without '?', the other print and the trend give 6.13 |

Print errors / print disagreements found in this pass:

- TP2049_tableV_stator8.csv row 5 DELTA INC: printed `5.13`; TM X-2926 Table V prints 6.13 for the same cell; every other row is 5.86-6.14 (neighbours 6.12, 6.14).
