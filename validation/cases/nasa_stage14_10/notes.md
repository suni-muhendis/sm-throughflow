# Stage 14-10 (NASA TM X-2645) transcription notes

Source: Urasek, Moore, Osborn, NASA TM X-2645 (1972), NTRS 19730002275, file
`TMX2645_sol13.pdf`. Stage 14-10 = rotor 14 + stator 10 (report p. 2, pdf p4:
"The stage is designated stage 14-10 with the rotor being rotor 14 and the
stator being stator 10"). Blade-tip solidity 1.3 member of the solidity series
(stage 12-5 at 1.7 is its reference 1).

## Files

- `TMX2645_tableI_design_overall.csv`: Table I (pdf p20). The table prints no
  units. WT FLOW kg/sec, RPM rev/min, TIP SPEED m/sec (appendix C); the two
  per-area flows are kg/sec/m2 (text p5).
- `TMX2645_tableII_rotor14_part1..4.csv`: Table II, rotor 14 design blade
  elements (pdf p21); the printed table is four stacked blocks, one CSV each.
- `TMX2645_tableIII_stator10_part1..4.csv`: Table III, stator 10 (pdf p22).
- `TMX2645_tableIV_rotor14_part1..3.csv`, `TMX2645_tableV_stator10_part1..3.csv`:
  blade geometry (pdf p23, side by side on one page), three blocks each.
- `TMX2645_fig1_flowpath_coordinates.csv`: the "Flow path coordinates" inset of
  Figure 1 (pdf p63). The printed down-arrows (value continues unchanged) are
  written as `↓`. Column FOOTNOTE holds the printed superscript `a`
  ("Instrumentation survey plane").

None of the tables print a units row; row 2 of each CSV is therefore empty.
Units (appendix C, pdf p17-18): RADII, RI, RO, chord, thicknesses, Z cm;
angles deg; VEL and SPEED m/sec; TEMP K; PRESS N/cm2.

## Uncertain cells ('?')

- Table II part4, RP 4, LOSS COEFF TOT: printed `0.0?3`, the middle digit is
  damaged (reads as 6 or 8). Transcribed `0.083?`. The ratio LOSS PARAM /
  LOSS COEFF of the neighbouring rows (0.216, 0.2125) with LOSS PARAM 0.018
  points to about 0.083-0.085; the text layer reads `0.0t,3`.
- Table IV part3, RP 1, TOTAL CAMBER: printed `11.52` or `11.32`; in this font
  3 and 5 are both flat-topped and the glyph is ambiguous at 8x zoom.
  Transcribed `11.52?`. KIC - KOC = 61.63 - 50.30 = 11.33 (all other rows
  satisfy TOTAL CAMBER = KIC - KOC within 0.01), and the pdftotext layer
  reads `11.32`, so the printed value is probably 11.32.

## Consistency checks run (all pass except the cells above)

Rotor: U = RPM*2*pi/60*r (16100 rpm), V^2 = Vm^2 + Vt^2, Vt = V sin(beta),
W^2 = Vm^2 + (U - Vt)^2, beta' = atan((U - Vt)/Vm), Mach ratios equal velocity
ratios, MERID VEL R = Vm_out/Vm_in; geometry radii equal Table II/III radii;
TOTAL CAMBER = KIC - KOC; SOLIDITY = N*chord/(2*pi*(RI+RO)/2) with N = 43 / 48.

## Conventions stated in the report

- beta (air angle) is the angle between the air velocity and the axial
  direction (appendix A, pdf p12). The relative meridional air angle based on
  the cone angle is printed as arctan(tan beta'_m cos alpha_c / cos alpha_s).
- KIC, KTC, KOC: angle between the blade mean camber line (at LE, transition
  point, TE) and the meridional plane (appendix C, pdf p17). The stator KOC is
  negative (camber line turned past axial).
- DELTA INC: difference between mean camber blade angle and suction surface
  blade angle at leading edge. CONE ANGLE: angle between the axial direction
  and the conical surface representing the blade element.
- PERCENT SPAN: percent of blade span from tip at rotor outlet.
- Blade elements are computed on conical surfaces and stacked on a line
  through the section centres of gravity (pdf p4).
- Axial positions: appendix A defines Z as "axial distance references from
  rotor blade hub leading edge"; Figure 1 labels its axis "Axial distance
  (referenced from rotor-blade-hub leading edge)". Appendix C defines
  ZIC/ZMC/ZTC/ZOC as "axial distance ... from inlet". The rotor hub row has
  ZIC = 0.000, and stator hub ZIC (7.529) minus rotor hub ZOC (4.259) = 3.27
  matches the stated 3.3 cm rotor-hub-TE to stator-hub-LE spacing, so the Z
  columns of Tables IV and V appear to share the rotor-hub-LE origin of
  Figure 1 (interpretation, not stated).
- ZTC is the axial distance to the MCA transition point; ZMC to the maximum
  thickness point. X FACTOR: ratio of suction-surface camber ahead of the
  assumed shock location of the MCA section to that of a DCA section.
  PHISS: suction surface camber ahead of the assumed shock location.
- Measurement stations (Figure 1, footnote a): station 1 Z = -2.540 cm,
  station 2 Z = 6.096 cm, station 3 Z = 13.462 cm. Station 3 combination
  probes were traversed circumferentially across one stator passage (7.5 deg)
  at nine positions (pdf p6-7). Data were translated from the measuring
  stations to the blade edges (pdf p8).

## Text facts (see scalars.json)

43 rotor / 48 stator blades, aspect ratios 2.4 / 2.0, MCA rotor and stator;
part-span damper at about 48 % span from the outlet rotor tip, max thickness
0.214 cm (damper geometry otherwise not given; figure 3 photograph only);
nominal cold (nonrotating, ambient) tip clearance 0.05 cm; no running
clearance given; no stator hub clearance stated (stator hubs seated on a
rubber O-ring in the inner casing).

## Figure only (not digitized)

Figure 1 flow path drawing (the coordinate inset is transcribed), Figure 2
facility, Figures 3-6 photographs and probe layout.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 2, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TMX2645_tableII_rotor14_part4.csv | 7 | LOSS COEFF TOT | `0.083?` | `0.083` | LOSS PARAM TOT = omega cos(REL BETAM OUT)/(2 sigma): 0.018 -> omega 0.081-0.085 (beta' 46.7, sigma 1.583); 0.063 would give 0.014 (relation reproduces rows 3 and 5) | 600-dpi zoom: middle glyph is a 6/8 with a broken upper loop; relation excludes 6, so 8 |
| TMX2645_tableIV_rotor14_part3.csv | 4 | TOTAL CAMBER | `11.52?` | `11.32` | TOTAL CAMBER = KIC - KOC = 61.63 - 50.30 = 11.33 (11.32-11.34 over rounding) | 600-dpi zoom: prints 11.32 clearly (the earlier 11.52 was a misread of the 3); relation agrees |

## Measured overall performance (Table VI)

NASA TM X-2645 Table VI, pdf p24-25 (printed 22-23), read from a 220-dpi render. One file per
speed, `TMX2645_tableVI_overall_<NNN>pct.csv`, readings as columns in printed order. The 60 and 50
percent parts (one reading each), where printed, are not transcribed.

| Speed | Readings |
|---|---|
| 70 % | 366, 367, 368, 369, 370 |
| 80 % | 364 |
| 90 % | 355, 356, 357, 358, 359 |
| 100 % | 350, 341, 342, 337, 343 |

Checks, all pass: temperature-rise efficiencies from the pressure and temperature ratios (the
stage efficiency uses the stage temperature ratio); constant annulus/frontal and orifice/frontal
flow ratios; ROTATIVE SPEED / PERCENT OF DESIGN SPEED 16089-16107 rpm; head-rise coefficient over
(PR^k - 1) times (N/N_design)^2 constant. Tables VII and VIII (blade elements) are not transcribed.
