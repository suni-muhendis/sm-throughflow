# naca_langley_3stage: transcription notes

Source: NACA RM L55G27 (Savage and Beatty, 1955). PDF page = printed
page + 1. Three transonic stages, no IGV, tip diameter 16 in. constant,
hub-tip 0.50 inlet to 0.75 exit, tip speed 1200 ft/s.

## TEST MEDIUM: FREON-12

All measured performance was obtained in Freon-12 at "Freon equivalent"
speeds (40-100 percent), converted to air-equivalent values by the method of
the report's ref. 14 (equal mean-radius rotor relative inlet Mach number and
inlet angle). A throughflow comparison in air at the air design point is not
the same experiment: the real-gas ratio of specific heats of Freon-12 differs
strongly from air, so the Mach-number distribution through the machine
differs. Treat the measured data with this in mind.

## Files

- `L55G27_tableI_velocity_diagram.csv`: per row, 3 radii (hub, mean, tip by
  inlet radius ratio ri/rt): exit radius ratio, inlet Mach number, inlet
  angle β, turning θ, axial-velocity ratio, Δp/(P-p)i, D-factor. Angles are
  relative for rotors (the table heading says β; Table III uses β').
- `L55G27_tableII_inner_contour_blockage.csv`: hub contour as axial station
  (in., from R1 inlet = 0.00) vs hub-tip ratio at the inlet (i) and exit (e)
  of every row, plus assumed and effective blockage (K) factors. With the
  constant tip radius 8 in., this gives the hub radius at each blade edge
  and the axial position of every LE/TE plane (stations are the design
  calculation planes; whether they coincide exactly with blade edges is not
  stated, but the labels R1-i, R1-e ... imply row inlet/exit).
- `L55G27_tableIII_blade_selection.csv`: per row at 3 conical-surface mean
  radii (ri + re)/2rt: relative inlet angle β', turning θ', NACA 65-series
  section designation, solidity, chord, setting angle β' − α' (from axis),
  Δα', Δα, Δθ'.

## Section designation

`65(17.5A10)10` = NACA 65-series, design lift coefficient 1.75 (Cl0 x 10 in
the parentheses), A10 mean line, 10 percent thick. `65(8.5A6I4b)08` uses the
A6I4b mean line, `65(4.7A2I8b)06` the A2I8b mean line (subscripts printed in
the original). S3 printed thickness digits 078 and 096 (7.8 and 9.6 percent).
The report (pdf p. 17) says Cl0 = 1.75 was used at the rotor 1 hub.

## Inconsistencies / interpretation notes

- Hub-tip ratios differ slightly between tables: Table I R1 exit .578 vs
  Table II R1-e .575; S1 inlet .606 vs .602; S1 exit .634 vs .629; R2 inlet
  .657 vs .651; R2 exit .692 vs .685; S2 inlet .712 vs .700; S2 exit .744
  vs .725; R3 inlet .750 vs .743. All cells re-read at zoom; kept as
  printed. Table I values are probably the effective (blockage-corrected)
  flow boundaries or earlier design iteration; the report does not say.
- Blade counts are NOT printed anywhere in the report. σ·2π·r/c with
  r = 8 (ri+re)/2rt in. gives integers consistently at all three radii:
  R1 14, S1 20, R2 17, S2 20, R3 19, S3 24 (interpretation, not a printed
  value; computed only to flag the gap).
- R2 and R3 sections other than the hub are "obtained from rotor 1 master"
  (tip cut off); their mean/tip profiles are therefore those of rotor 1 at
  the corresponding span on the master, not listed explicitly.
- Stator 1 was built with hub and tip settings interchanged (fabrication
  error); Table III Δα' and Δα reflect that; the "Blade setting angle"
  column is therefore presumably the as-designed value. Check before use.

No cell is marked '?'.

## Missing

- Blade counts (see above), edge radii (only TE radius = 10 percent of max
  thickness), stacking.
- Flowpath: Table II gives hub contour points; tip constant 8 in. Fig. 1 (pdf
  p. 43, "Schematic drawing of three-stage transonic compressor") figure
  only. Fig. 9 test layout figure only.
- Rotor tip clearance measured values: only "generally close to design
  values" (0.030 in.).
