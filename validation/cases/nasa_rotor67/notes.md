# NASA Rotor 67 alone (NASA TP-2879)

Source: Strazisar, Wood, Hathaway, Suder, NASA TP-2879, 1989, NTRS 19900001929.
Rotor 67 is the first-stage rotor of the low-aspect-ratio two-stage fan of NASA TP-1493
(`../nasa_2stage_fan_r67/`), tested here alone (stator removed, no IGV).

## Transcribed

- `TP2879_tableII_flowpath.csv`: Table II, inner and outer flowpath coordinates, K = 1..80
  (printed as two side-by-side column sets, merged). Units not printed in the table; cm per the text.
- `TP2879_tableIV_geometric_parameters.csv`: Table IV, design-streamline radii, annular area
  elements and streamline slopes at survey stations 1 and 2 (9 design streamlines; the headnote
  about 1.5 % hub / 1.26 % tip blockage is in `source.json`).
- `scalars.json`: blade count (22), clearance, design point, geometry facts, station positions.

No cell is marked `?`; the print is clean.

## Not transcribed (by instruction)

Table I, "BLADE SURFACE COORDINATES ON SURFACES OF REVOLUTION", PDF pages 22-36 (printed 18-32):
14 sections ("SURFACE NUMBER n FROM THE HUB"), each with LE/TE circle data and 35 surface points.
This is the hot (design-speed) shape: NASTRAN deflections applied to manufacturing coordinates,
then corrected by a 1.4 deg restagger toward closed at the tip to match laser measurements of the
blade tip (p7). Section 14 lies outside the physical tip; actual tip = section 14 minus 1.0 mm normal
to the shroud. Nomenclature in Fig. 4 (PDF p52, figure only).

## Conventions

- Z origin (blade geometry and flowpath): intersection of the blade leading edge with the hub (p6-7).
- LA / aerodynamic-survey axial coordinate AP differs: AP = Z_blade - 2.159 cm (p11). Fig. 5 (PDF p53)
  labels aero station 1 at AP = -4.632 cm, the rotor hub LE at AP = -2.159 cm, aero station 2 at
  AP = 8.852 cm. Hence station 1 at Z = -2.473 cm and station 2 at Z = 11.011 cm (derived, not printed).
- Spanwise locations are measured from the tip (p6).
- The rotor geometry is the TP-1493 rotor 1 geometry in hot running shape; TP-1493 Table III gives the
  design blade-element description of the same rotor (cold/hot status not stated there).

## Consistency with TP-1493

TP-1493 Fig. 1 gives the two-stage fan flowpath as a coarse box (Z from the same hub-LE origin,
3 decimals); TP-2879 Table II is a finer 80-point description of the rotor-region flowpath
(Z -18.06 to 35.44 cm). Not compared numerically here. The tip clearances differ in the two
reports: TP-1493 says the rotating clearance was calculated as 0.04 cm; TP-2879 says the running tip
clearance is approximately 1.0 mm (different builds/tests).

## Figures only

Fig. 3 velocity diagrams at 10 % span (p51), Fig. 4 geometry nomenclature (p52), Fig. 5 meridional
view with LA and survey locations (p53; only the three AP labels were taken).
