# Stage 12-5 (NASA TM X-2658) transcription notes

Source: Moore and Reid, NASA TM X-2658 (December 1972), NTRS 19730006256,
file `TMX2658_sol17.pdf`. "The stage presented in this report has been
designated stage 12-5, with the rotor being rotor 12 and the stator being
stator 5" (pdf p5). It is the tip-solidity 1.7 member of the 1.3/1.5/1.7
series, which keeps "the same velocity diagrams and flow path" and varies the
blade count (pdf p5).

## Files

- `TMX2658_tableI_design_overall.csv` (pdf p22). No units printed.
- `TMX2658_tableII_rotor12_part1..4.csv` (pdf p23), four stacked blocks.
- `TMX2658_tableIII_stator5_part1..4.csv` (pdf p24).
- `TMX2658_tableIV_rotor12_part1..3.csv` (pdf p25).
- `TMX2658_tableV_stator5_part1..3.csv` (pdf p26).
- `TMX2658_fig1_flowpath_coordinates.csv` (Figure 1 inset, pdf p66). Read
  from this report's page; every value is identical to the Stage 14-10 inset
  (TM X-2645), as expected for the common flow path. `↓` = printed down-arrow
  (value continues unchanged); FOOTNOTE `a` = instrumentation survey plane.

The tables print no units row (row 2 empty). Units per appendix C (pdf
p19-20): radii, chord, thicknesses, Z in cm; angles deg; velocities m/sec;
temperature K; pressure N/cm2.

## Uncertain cells

None marked '?'. Every row passed: U = omega r at 16100 rpm, V^2 = Vm^2 +
Vt^2, W and beta' from the triangle, Mach ratios = velocity ratios, MERID VEL
R, TOTAL CAMBER = KIC - KOC, SOLIDITY = N c / (2 pi r_mean) with N = 56 / 62,
geometry radii = blade-element radii. Table V TIP PERCENT SPAN is printed `0`
without a decimal point (other rows `5.`, `10.`); kept as printed.

## Text facts and gaps

- 56 rotor / 62 stator blades, aspect ratio 2.4 / 2.0, MCA both rows, rotor
  tip diameter 50.8 cm.
- Rotor part-span damper at about 48 % span from the tip. **Damper thickness
  and geometry not given** (figure 3 photograph only).
- **No tip clearance is stated in this report.**
- Stator blades supported on the outer surface only (no hub clearance given).
- Station 3 combination probes traversed 5.8 deg (one stator gap).
- Survey planes Z = -2.540, 6.096, 13.462 cm (Figure 1 inset footnote a).

## Conventions

Same as TM X-2645: beta measured from the axial direction; KIC/KTC/KOC from
the meridional plane; percent span from the tip at rotor outlet; sections on
conical surfaces approximating stream surfaces, stacked on a radial line
through the centres of gravity; Figure 1 Z referenced from the rotor-blade-hub
leading edge; ZIC..ZOC defined in appendix C as "axial distance ... from
inlet". Rotor hub ZIC = 0.000 and stator hub ZIC - rotor hub ZOC = 7.647 -
4.345 = 3.30 cm, consistent with the Z columns sharing the rotor-hub-LE origin
(interpretation; not stated).

Although the series keeps the flow path, the design blade-element radii of
rotor 12 / stator 5 differ from rotor 14 / stator 10 in the third decimal at
several RPs, and the blade-edge axial positions differ (e.g. stator hub ZIC
7.647 here vs 7.529 for stator 10).

## Figure only

Figure 1 drawing, Figure 2 facility, Figures 3-6 photographs and probe layout.
