# naca_inlet_stage: transcription notes

NACA Lewis transonic inlet stage (no IGV, 21-blade transonic rotor, 18-blade
subsonic circular-arc stator, tip diameter 17.36 in.). Sources:
RM E52A24 (design, Part I), RM E52C27 (blade coordinates, Part II),
RM E53G17 (blade-row performance, Part III). Not used here: RM E54C26
(Part IV) and RM E56J17 (Part V).

## Files

- `E53G17_tableI_rotor_blade_element_geometry.csv`: 5 rotor elements at
  radial positions 4-8 (equally spaced across the passage; 4 and 8 are just
  outside the wall boundary layers): inlet radius r3, outlet radius r4,
  solidity, blade inlet/outlet angle γ°3, γ°4.
- `E53G17_tableII_stator_blade_element_geometry.csv`: 4 stator elements at
  the wake-rake positions 1-4 (radius equal at inlet and outlet).
- `E52C27_fig1_rotor_hub_contour.csv`: hub contour under the rotor (N, R)
  from Fig. 1 (N measured axially along the hub from the rotor leading-edge
  end, as drawn; R hub radius). R from 4.475 at N = 0 to 5.140 at N = 3.06.
- `E52C27_fig2_rotor_section{B,C,D,E}.csv` + `..._section_parameters.csv`:
  rotor design coordinates at four planes perpendicular to the radial
  stacking line (fabrication coordinates, transformed graphically from the
  conical design sections). X along the chord line from the LE, YU / YL
  upper and lower surface ordinates from the chord line. F = distance along
  chord from LE to the stacking point, G = offset of the stacking point from
  the chord line, α = angle between chord and axis (sketch, Fig. 2).
- `E52C27_fig4_rotor_hub_measured_sectionG.csv`: measured (optical
  comparator) hub profile in a plane parallel to the blade base; LE radius
  4.824 in., TE radius 5.394 in.; chord inclined 23 deg to the axis (sketch).
- `E52C27_fig6_stator_section{B,C}.csv` + parameters: stator coordinates at
  B-B (tip, near the 8.68 R outer arc) and C-C (hub, 5.20 R), same
  F, G, α convention.

## Section heights (Fig. 1 of E52C27)

The rotor sections B-B, C-C, D-D are dimensioned 4.688, 2.598 and 1.138 in.
above the bulb centreline, whose radius is 3.992 in. (Fig. 1 caption), i.e.
the planes are at about r = 8.680, 6.590, 5.130 in. A further label 0.502
is drawn near E-E/the bulb CL; whether it locates E-E (r = 4.494) or the
bulb top cannot be decided with certainty from the sketch. These radii are
interpretations, not printed values.

## Conventions

- E53G17: γ° = direction of tangent to mean camber line at LE or TE; flow
  angles β, β' from the axis of rotation. Station 3 rotor inlet, 4 rotor
  outlet / stator inlet, 5 stator outlet. Hub radii 4.312 (st. 2), 4.411
  (3), 5.186 (4, 5, 6) in.
- Rotor sections were designed on conical stream surfaces (E52A24 p. 4);
  E52C27 Fig. 3 gives measured rotor mean-line angles vs radius and Fig. 7
  stator mean-line angles (curves only, not digitized: figure only). E52C27
  says measured rotor inlet angles are about 2 deg higher than the design
  values of E52A24 fig. 8(b).
- Stator: linear fairing between circular-arc hub and tip sections.

## Inconsistencies / reading notes

- Rotor Fig. 2: sections D-D and E-E both print α = 23° 15'. Re-read at
  zoom; both clearly read 23° 15'. Possibly a drafting repeat; kept.
- Section E-E starts at YU = YL = 0.061 and goes negative aft (YU -.455 at
  the TE): the section's chord datum differs from the other sections
  (strong camber at the hub). Kept as printed.
- Stator B-B last X printed "3!210"; read 3.210.
- Design (E52A24) vs measured (E52C27) t/c: rotor 0.06/0.085 design vs
  0.048 tip / 0.075 hub measured; stator 0.06 hub/0.08 tip design vs 0.065
  hub/0.084 tip measured.
- Design stator hub radius 5.2 in. (E52A24) vs inner casing 5.186 in.
  (E52C27, E53G17).

No cell is marked '?'.

## Missing

- Axial positions of the blade rows relative to a datum: only the rotor
  axial extent (3.060 in. in the Fig. 1 plan view, 1.542 in. LE to stacking
  line), and the axial rotor-stator clearance at the hub (1.75 in.). The
  stator axial position is not otherwise given. The test-rig sketch
  (E53G17 Fig. 2) is figure only.
- Rotor blade-element data at the E52C27 planes are in rectangular
  fabrication coordinates, not on stream surfaces; the E53G17 Table I gives
  blade angles on the five streamlines.
- Velocity diagrams (E52A24 Fig. 2) and blade profile sketches (Fig. 3):
  figure only.
