# NASA Lewis Low-Speed Axial Compressor (LSAC): transcription notes

Sources: NASA TM-4635 (Wasserbauer, Weaver, Senyitko, July 1995, corrected copy; facility
description) and NASA CR-198536 (Wellborn and Okiishi, October 1996; shrouded-stator cavity
experiments). All PDF page numbers are 1-based PDF indices.

## What is here

| Content | File |
|---|---|
| Overall design parameters, blade counts, chords, setting angles, gaps, clearances | `TM4635_tableI_design_parameters.csv` (PDF p. 4), `CR198536_tableIII1_baseline_parameters.csv` (PDF p. 29) |
| Probe survey stations: axial position (m) and circumferential positions | `TM4635_tableII_probe_survey_stations.csv` (PDF p. 11) |
| Measured stator seal-tooth clearances, per stage and nominal, Part 1 tests | `CR198536_tableV1_seal_tooth_clearances_part1.csv` (PDF p. 43) |
| Measured stage 3 seal-tooth clearances, Part 2 tests | `CR198536_tableV2_seal_tooth_clearances_part2.csv` (PDF p. 43) |
| Text values (speeds, coefficients, profile types, stacking, overcamber, twist, stations, blading origin) | `scalars.json` |

Neither table I nor table III.1 prints column headings; `GROUP,ITEM,VALUE,UNIT` was added by the
transcriber, with the unit split off the value cell exactly as printed. No cell is marked `?`:
every number in these tables is clean typeset print.

## Figure-only geometry (not digitized)

- CR-198536 Fig. III.1 (PDF p. 28): meridional view of stage 3 with stations 3.0, 3.5 and 4.0,
  hub, foot-ring, seal tooth and cavities. No dimensions.
- CR-198536 Fig. III.2 (PDF p. 30): drawing of the whole rig (bellmouth, bullet nose, trip strip,
  IGV, compressor, exit diffuser). No dimensions.
- CR-198536 Fig. III.4 (PDF p. 32): rotor airfoil sections at 10, 50 and 90 % span, drawn on
  x/y axes in cm (stacking axis marked). Plotted shapes only.
- CR-198536 Fig. III.5 (PDF p. 33): radial distributions of rotor solidity and aspect ratio, NASA
  vs GE (percent span vs "Blade Ratios").
- CR-198536 Fig. III.6 (PDF p. 33): radial distributions of rotor leading-edge, trailing-edge and
  setting angles, NASA vs GE.
- CR-198536 Fig. III.8 (PDF p. 34): stator airfoil sections at 10, 50 and 90 % span (cm axes,
  stacking axis marked).
- CR-198536 Fig. III.9 (PDF p. 35): radial distributions of stator solidity and aspect ratio.
- CR-198536 Fig. III.10 (PDF p. 35): radial distributions of stator leading-edge, trailing-edge
  and setting angles.
- CR-198536 Figs. III.3 and III.7: photographs of the rotor and stator blades.
- CR-198536 Fig. IV.1 (PDF p. 40): seal-tooth control-volume schematic; Fig. V.1 (PDF p. 42):
  cavity configurations (wood extensions, balsa/cherry strips, shims); Fig. VIII.1 (PDF p. 92):
  probe axial positions in the stator 3 cavities, scaled probe sizes, no numbers.
- TM-4635 Fig. 3 (PDF p. 6): survey-station layout (legend only; axial positions are in Table
  II); Fig. 2 (PDF p. 5): diffuser geometry; Fig. 6 (PDF p. 8): stator footring with labyrinth seal
  (no dimensions); Figs. 8-11: probe sketches with probe dimensions (not
  flowpath geometry, not transcribed).

## Missing

- No per-section blade geometry is tabulated in either report (no metal angles, camber, chord,
  solidity, thickness, edge radii per radius). Only midspan chord and setting angle (Table I /
  III.1) and the figures above. The base design (GE Rotor B / Stator B) is documented in
  Wisler, NASA CR 135391 (CR-198536 ref. [15]); NASA's rotor angles differ from GE's away from
  the hub and the stator has an added linear twist (about 1.2 deg at the tip), so CR 135391
  tables are not the LSAC geometry as built.
- No flowpath coordinates: the annulus is given only by tip/casing radius and hub radius
  (constant-radius annulus is implied by the single values, not stated).
- No cavity or seal-tooth dimensions (cavity depth, width, seal-tooth knife thickness) are
  printed; nomenclature lists "b = seal-tooth knife thickness" but no value is given.
- The axial-position zero of TM-4635 Table II is not stated. Printed spacings: 0.096-0.097 m
  between successive stations from 1.5 to 4.5; 0.144 m from 1.0 to 1.5 (rotor 1 with casing
  treatment); 0.206 m from 0.5 to 1.0; 0.183 m from 4.5 to 5.0.
- The angle reference for "blade setting angle" (from axial or from tangential) is not stated in
  either report.
- No IGV geometry beyond the blade count (52) is printed.
- Hot vs cold (running vs static) clearance: CR states the seal-tooth clearances were measured
  statically; no running values. Rotor tip clearance conditions are not stated.

## Inconsistencies between and within the reports (copied as printed)

- Rotational speed: TM Table I 980 rpm; CR Table III.1 958 rpm. Tip speed: TM 61.0 m/sec,
  CR 61.15 m/s "based on casing radius". 958 rpm at r = 60.96 cm gives 61.15 m/s; 980 rpm at
  61.0 cm would give about 62.6 m/s, so TM's tip speed and speed are not consistent with each
  other.
- Tip radius: TM 61.0 cm; CR 60.96 cm. Span: TM 12.2 cm; CR 12.19 cm.
- Rotor tip clearance: TM 0.17 cm (1.40 % span); CR 1.7 mm (1.4 % span) - same value.
- Stator seal clearance: TM 0.09 cm (0.78 % span); CR Table III.1 0.85 mm (0.70 % span).
  CR Table V.1 baseline nominal (four-stage average, measured) is 0.56 % and stage 3 is 0.69 %;
  CR Table V.2 baseline stage 3 is 0.71 %. So the "baseline" seal clearance differs among
  TM Table I, CR Table III.1 and CR Tables V.1/V.2.
- CR Table V.1 Nominal column agrees with the mean of the four stages to two decimals for every
  row (checked arithmetically).
- The text layers of both PDFs scramble Table II (TM) and Table III.1 (CR); everything was read
  from the 200 dpi images.

## Conventions

- Spanwise positions in CR-198536 are percent span from the hub.
- TM Table II circumferential positions: "Looking downstream; top=0°".
- Station numbering (TM Fig. 3): 0.5 IGV inlet, 1.0 rotor 1 inlet, x.5 rotor x exit, (x+1).0
  rotor x+1 inlet, 5.0 compressor exit. CR uses 3.0 / 3.5 / 4.0 as rotor 3 inlet / stator 3
  inlet / stator 3 exit.
- Stators are hub-shrouded (footring) with one labyrinth seal tooth; stator blade ends were
  sealed at hub and casing in all CR tests. Rotor 1 has circumferential-groove casing treatment.
