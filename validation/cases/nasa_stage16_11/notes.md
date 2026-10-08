# Stage 16-11 (NASA TM X-2904) transcription notes

Source: Moore, Urasek, Kovich, NASA TM X-2904 (November 1973), NTRS
19740001906, file `TMX2904_fan178.pdf`. "The stage presented in this report
has been designated "stage 16-11" with the rotor being rotor 16 and the
stator being stator 11" (pdf p4).

## Files

- `TMX2904_tableI_design_overall.csv` (pdf p22). No units printed.
- `TMX2904_tableII_rotor16_part1..4.csv` (pdf p23), four stacked blocks.
- `TMX2904_tableIII_stator11_part1..4.csv` (pdf p24).
- `TMX2904_tableIV_rotor16_part1..3.csv` (pdf p25).
- `TMX2904_tableV_stator11_part1..3.csv` (pdf p26).
- `TMX2904_fig1_flowpath_coordinates.csv` (Figure 1 inset "Flow path
  coordinates", pdf p65). `↓` = printed down-arrow; FOOTNOTE `a` =
  "Measuring station". This flow path differs from the 14-10/12-5/8-8 one
  (casing 25.400 -> 25.336 at z = 0 -> 24.384; hub 12.668 at z = 0, 15.240
  from z = 10.973).

Tables print no units row (row 2 empty); units per appendix C (cm, deg,
m/sec, K, N/cm2).

## Uncertain cells

None marked '?'. All rows pass the consistency checks (U = omega r at
16100 rpm, velocity triangles, Mach ratios, MERID VEL R, camber = KIC - KOC,
solidity with N = 44 / 48).

Observation: Table I gives WT FLOW 26.535 kg/sec and TIP SPEED 424.943 m/sec;
the text rounds to 26.5 kg/sec and 425 m/sec. Rotor TIP RI 25.204 is below
the casing radius 25.336 at z = 0 and the rotor TIP ZIC is 1.016 cm, where the
casing (25.336 at z = 0, 24.638 at z = 4.064) is about 25.16 by linear
interpolation; not resolved, transcribed as printed.

## Text facts (scalars.json)

44 rotor / 48 stator blades, AR 2.6 / 2.3; MCA both rows; tip solidity 1.3
for both rows; damper at about 50 % span from the outlet rotor tip, max
thickness 0.215 cm (no other damper geometry; photograph only); nominal
0.050 cm radial tip clearance at ambient nonrotating conditions (no running
value); rotor hub TE to stator hub LE 3.148 cm (0.7 rotor tip chord) -
consistent with stator hub ZIC 7.125 - rotor hub ZOC 3.977 = 3.148; station
3 traverse 7.5 deg (one stator passage); survey planes Z = -2.540, 5.080,
12.700 cm. Annulus area at rotor LE 0.149 m2, frontal area 0.199 m2.

## Conventions

beta from the axial direction; KIC/KTC/KOC between the mean camber line and
the meridional plane; PERCENT SPAN from tip at rotor outlet; blade elements
on conical surfaces stacked through the centres of gravity; Figure 1 Z from
the rotor blade hub leading edge; ZIC..ZOC defined in appendix C as "axial
distance ... from inlet" (rotor hub ZIC = 0.000, consistent with the
rotor-hub-LE origin; interpretation).

## Figure only

Figure 1 drawing (inset transcribed), Figure 2 facility, Figures 3-6.
