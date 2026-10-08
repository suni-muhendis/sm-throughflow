# naca_10stage: transcription notes

Sources: NACA RM E52B18 (design, Johnsen 1952) and NACA RM E53H10 (IGV
sketch, Budinger and Serovy 1954). PDF page = printed page + 1 in RM E52B18;
PDF page = printed page + 2 in RM E53H10.

## What is in the tables

- `E52B18_tableI_blade_data.csv`: per row (rotor/stator 1-10, exit vane): hub
  radius at entrance, blade count, chord (constant along span), axial
  projection of chord at hub radius, design camber CL,i (constant along span),
  maximum thickness in percent of chord (10 everywhere).
- `E52B18_tableIIa_rotors.csv`, `E52B18_tableIIb_stators.csv`: five equally
  spaced radii per row at the row entrance. The printed station number appears
  only on the first of five lines; it is repeated on every line here.
  Station 1, 3, ... 19 = ahead of rotor 1..10; 2, 4, ... 20 = ahead of
  stator 1..10 (E52B18 symbol list). Z = r/r_tip (tip radius 10 in.), so
  r = 10 Z in. The hub Z equals Table I hub radius / 10 for every row.
- `E53H10_fig2_igv_blade_coordinates.csv`: IGV radius, camber angle μ, chord
  c and solidity at 0.25-in. radius steps (inset table of Fig. 2).

## Symbols and conventions (RM E52B18 pp. 2-4)

- X: circumferential component of absolute velocity of entering air / rotor-tip
  speed; Y: change in circumferential component / rotor-tip speed; h: axial
  velocity / rotor-tip speed; Z: blade-element speed / tip speed (= radius
  ratio). All velocities nondimensionalised by Ut = 869 ft/s.
- β, β': absolute and relative inlet-air angles measured from the axis (deg).
  α: angle of attack (deg), i.e. relative to the blade chord of the 65-series
  section (NACA cascade convention). Δβ: turning angle; Δh change of h through
  the row.
- The tables give no blade metal angles or stagger. The report states
  (p. 18) that stagger and turning were established first and α from
  Δβ = mα + b; stagger = β (or β') − α is the cascade relation implied, but it
  is not printed and is left to the interpretation step.
- Numerical relations that the printed rotor rows satisfy (verified for all
  50 rotor lines): W/Ut = sqrt((Z−X)² + h²), tan β' = (Z−X)/h, exit relative
  angle atan((Z−X−Y)/(h+Δh)) = β' − Δβ. The report's text (p. 14) writes
  (W/Ut)² = (X+Y)² + h² for the rotor inlet, which does not match its own
  table (apparently a typo copied from the stator formula). Stators satisfy
  V/Ut = sqrt((X+Y)² + h²), tan β = (X+Y)/h, exit angle atan(X/(h+Δh)) =
  β − Δβ (all 50 lines). For stators X is therefore the swirl leaving the
  stator (= entering the next rotor) and X+Y the swirl entering the stator.
- Solidity σ = N c / (2π r) with Table I N and c agrees with every printed σ
  to within 0.0012 except two lines (below).

## Cells that disagree with the checks (kept as printed, re-read at 3x zoom)

- Rotor station 1, Z = 1.0000: β' printed 46.20; from Z, X, h it is 46.15.
  Δβ printed 7.54 (computed 7.50); W/Ut .8151 is consistent. The 0.05 deg
  offset is in the report, not a reading error.
- Rotor station 13, Z = 0.8361: β' printed 38.97; computed 38.94.
- Rotor station 1, Z = .8875: σ printed .697; N c/(2π r) = .6949.
- Rotor station 13, Z = 0.8361: σ printed 1.094; N c/(2π r) = 1.0964.
- Stator station 16, Z = .9693: X printed with a stray leading dot
  ("..2676"); transcribed as .2676 (consistent with V/Ut and β).

No cell is marked '?'.

## Inlet guide vanes

- 36 circular-arc, constant-thickness sheet-metal vanes, No. 14 gage
  (0.083 in.) mild steel (E53H10 p. 3 and Fig. 2).
- Fig. 2 (pdf p. 20) is a sketch with labels: "3.75\" rad." (arc radius
  dimension on the camber-line sketch), "0.03\" rad." (leading edge),
  trailing-edge detail "0.25\"" and "0.020" (taper length and edge
  thickness by the look of the sketch), planform "1.78\"" (width near the
  base) and "10.00\" rad." The planform drawing shows a straight leading edge
  and a chord increasing toward the tip; exactly what "1.78\"" and
  "10.00\" rad." dimension cannot be stated with certainty from the drawing.
  Note that the tabulated chord at 5.25 in. is 1.134 in., not 1.78.
- The inset table gives μ (camber angle), c, σ from r = 5.25 to 10.00 in.;
  σ printed only every 1 in. ("-----" elsewhere). Hub radius at IGV is not
  stated, the table starts at 5.25 in. while rotor 1 hub radius is 5.500 in.
- The sketch defines φ and i relative to the inflow V; no stagger/setting
  angle is tabulated. RM E53H10 tested 0 deg (original) and −5 deg (reset)
  incidence. E53H10 p. 5 says the vanes were designed with the
  design rule for convergent annuli of its ref. 7.
- IGV exit/turning design data are not tabulated in E52B18 (Table II starts at
  station 1, rotor 1 inlet, whose X gives the IGV exit swirl).

## Missing / not tabulated

- Axial positions of blade rows (LE/TE), axial gaps, and flowpath
  coordinates: not tabulated anywhere in RM E52B18 or E53H10. Table I gives
  the hub radius at the entrance of each row and the axial projection of the
  chord at the hub; the tip radius is constant 10 in.
- Flowpath drawing: RM E53H10 Fig. 1 (pdf p. 19, printed 17), "Cross-sectional
  view of 10-stage compressor showing instrumentation stations": schematic,
  no dimensions (figure only). RM E52B18 has no flowpath figure (its figures
  are design charts, pressure-ratio and axial-velocity plots, and the
  performance map).
- Tip/hub clearances: not given in E52B18 or E53H10.
- Exit vane: only Table I data (no Table II line; station 21 data absent).
- Measurement stations in E53H10 use a different numbering (1 after IGVs,
  3 after first stator, 22 after exit vanes; Fig. 1) from E52B18.
