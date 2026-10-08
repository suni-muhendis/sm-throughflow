# Stage 6-1 (NASA TM X-2731) transcription notes

Source: Kovich and Reid, NASA TM X-2731 (March 1973), NTRS 19730011268, file
`TMX2731_MCA419.pdf`. "This compressor stage is designated stage 6-1" (pdf p5);
rotor 6 and stator 1 (pdf p6, tables II-V).

## Files

- `TMX2731_tableI_design_overall.csv` (pdf p23). No units printed.
- `TMX2731_tableII_rotor6_part1..4.csv` (pdf p24), four stacked blocks.
- `TMX2731_tableIII_stator1_part1..4.csv` (pdf p25).
- `TMX2731_tableIV_rotor6_part1..3.csv` (pdf p26).
- `TMX2731_tableV_stator1_part1..3.csv` (pdf p27).
- `TMX2731_fig1_flowpath_coordinates.csv` (Figure 1 "Compressor flow path",
  pdf p64): coordinate box with its own units row (cm). `↓` = printed
  down-arrow (value continues unchanged). This flow path is **different**
  from the 14-10 / 12-5 / 8-8 flow path (hub r = 8.763 at z = -15.24; casing
  contracts from 25.400 to 24.625 cm over the rotor).

Tables print no units row (row 2 empty); units per appendix C (cm, deg,
m/sec, K, N/cm2).

## Uncertain cells

- Table II part4, RP 9, LOSS COEFF PROF: printed `..075` (leading `0`
  smudged). Transcribed `0.075?`.
- Table V part1, HUB KTC: printed `1P.10`, read as 18.10 (neighbours 18.18,
  18.25; no '?' because 8 is the only digit that fits the glyph).

All rows pass the consistency checks (U = omega r at 16000 rpm, velocity
triangles, Mach ratios, MERID VEL R, camber = KIC - KOC, solidity with
N = 47 / 60).

## Remarks / inconsistencies noticed

- The catalogue lists the rotor blade count as "–"; the report gives 47
  rotor blades (pdf p6).
- Rotor TIP RI (Tables II/IV) = 25.024 cm at ZIC = 0.773 cm, whereas the
  Figure 1 casing is 25.400 at z = 0 and 25.146 at z = 1.83 (about 25.29 at
  the LE axial position). The rotor TE tip (RO 24.938 at ZOC 3.055) matches
  the casing (24.943 at z = 3.05). Not resolved; both as printed. The TIP
  cone angle (-2.167) is also smaller in magnitude than at RP 1 (-5.794).
- Stator hub ZIC 7.690 - rotor hub ZOC 3.745 = 3.945 cm vs the stated rotor
  hub TE to stator hub LE spacing of 3.86 cm (text). Both as printed.

## Text facts (scalars.json)

47 rotor / 60 stator blades, AR 2.5 / 2.2; MCA both rows; rotor tip solidity
1.3, stator hub solidity 2.0; damper at about 45 % span from the outlet
rotor tip, max thickness 0.19 cm (no other damper geometry; photograph
only); nominal cold tip clearance 0.05 cm at ambient conditions (no running
value); survey stations z = -1.91, 5.78, 12.95 cm (Figure 1 labels);
station 3 traverse one stator passage (6.0 deg).

## Conventions

As in the other Lewis single-stage reports: beta from the axial direction;
KIC/KTC/KOC between the mean camber line and the meridional plane; PERCENT
SPAN from the tip at rotor outlet; conical blade sections stacked through the
centres of gravity; Figure 1 z from the rotor hub leading edge; ZIC..ZOC
defined as "axial distance ... from inlet" (rotor hub ZIC = 0.000, consistent
with the rotor-hub-LE origin; interpretation).

## Figure only

Figure 1 drawing (coordinate box transcribed), Figure 2 facility, Figures
3-6 photographs and probe layout.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 1, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TMX2731_tableII_rotor6_part4.csv | 12 | LOSS COEFF PROF | `0.075?` | `0.075` | column printed as 0.xxx throughout; LOSS PARAM PROF/TOT = .016/.023 gives PROF coefficient 0.071-0.079 from TOT 0.108 | 600-dpi read: digits 075 clear, only the leading 0 is smudged (prints as '..075'); value 0.075 |
