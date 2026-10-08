# naca_8stage: transcription notes

Sources: NACA RM E53I24 (original design, Voit 1953; PDF page = printed
page + 1) and NACA RM E55B28 (modified design, Geye and Voit 1955; PDF page =
printed page + 1). RM E55A03 (performance of the modified machine) was opened
for facts only.

## Original design (RM E53I24)

- `E53I24_tableI_design_data.csv`: stage design data. The "Subsonic stages"
  block lists stages 1-9 of the original nine-stage subsonic design (ref. 6,
  NACA TN 2589). The two transonic stages replaced the front of that design
  (the report says the over-all pressure ratio of the eight stages is about
  that of the original nine subsonic stages). Table II tip h of stages 3-8
  (.4178, .4360, .4570, .4815, .5000, .5000) equals Table I subsonic h_t of
  stages 3-8, so stage n of this compressor = subsonic-design stage n for
  n = 3-8; subsonic-design stage 9 is not used. The report does not state
  this mapping in words.
- `E53I24_tableIIa_vector_rotor.csv`, `E53I24_tableIIb_vector_stator.csv`:
  entrance vector data at 5 radii per row, Z = r/r_t, r_t = 10 in.
- `E53I24_tableIIIa_blade_rotor.csv`, `E53I24_tableIIIb_blade_stator.csv`:
  blade design data: radius ratio, blade count, chord, solidity, design camber
  (CL,i for 65-series rows, φ for circular-arc transonic rotors 1-2),
  thickness (percent chord), angle setting ψ (chord to compressor axis).
  Rotors 1-3 and stators 1-3 have 5 radii; rows 4-8 have 3.

### Checks and inconsistencies (all cells re-read at 1.7x zoom; kept as printed)

- Rotor Table II: V'/Ut = sqrt((Z−X)² + h²) holds for all 40 lines. For the
  transonic stage 1 tip line, β' = atan((Z−X)/h) = 63.61 holds, but for most
  other lines the printed β' and Δβ' differ from atan((Z−X)/h) by 0.1-1 deg
  (stage 1) and up to ~1.5 deg (subsonic stages). The report explains (pdf
  p. 18): subsonic-stage angles in Table II are "effective angles" based on
  the average axial velocity across the row; transonic angles are along an
  assumed streamline (flow conditions entering and leaving a row computed
  along streamlines, not at constant radius, pdf p. 16). So the mismatch is
  by construction, not a transcription error.
- Stator Table II: V/Ut = sqrt(X² + h²) holds for stages 1-2 and the tip
  lines; for stages 3-8 the printed V/Ut and β differ from the vector
  relation in the same way (effective angles). Not errors in reading.
- Stator Table III solidity = N c /(2π · 10 Z) checks for every line.
- Rotor Table III: rotors 3-8 check; rotor 1 does not (printed 1.186 ...
  1.864 vs 1.199 ... 1.999 from N c/(2π 10 Z)), and rotor 2 lines .9233 and
  .7465 differ by about 0.01. The transonic rotor sections are on streamline
  surfaces and the Table III radius ratios of rotors 1-2 (e.g. .8990, .7840,
  .6500 for rotor 1) are not the Table II radius ratios (.8700, .7400,
  .6100); presumably σ uses a mean radius along the streamline. Kept as
  printed.
- Stator 1 Z=.8941 setting angle printed "21:3" with a smudged point; read
  as 21.3. Stator Table II stage 5 Δβ "21..70" read as 21.70; stage 6 X
  ":6813" read as .6813. Not marked '?' because the digits are clear.

No cell is marked '?'.

### Conventions

- β, β' measured from the axis; ψ = angle between chord and compressor axis;
  φ = camber (included angle of circular-arc mean line); D, D' = diffusion
  factors. Station numbering in scalars.json.
- Velocities are ratios to rotor tip speed U_t.

### Missing

- Axial positions of rows, chord axial projections, hub radii in inches,
  flowpath coordinates: not tabulated. The hub radius at each row entrance
  follows from the hub Z of Table II times 10 in. (tip radius constant 10
  in.). The flowpath is drawn only in Fig. 3, "Diagramatic sketch of
  compressor flow passage and blading" (pdf p. 29, printed 28), figure only.
- Boundary-layer blockage distribution: Fig. 2 (figure only).
- Tip clearances: not given.
- Exit guide vanes: mentioned (pdf p. 10) but no geometry tabulated.
- Transonic rotor LE/TE radius 0.020 in.; edge radii of 65-series rows not
  stated.

## Modified design (RM E55B28)

The task note said E55B28 contains "stator reset changes". It does not:
RM E55B28 states (pdf p. 3) that several stator rows had been reset after
the first tests, but that blading was destroyed by a fatigue failure and the
reset angles are not given. The rebuilt ("modified") compressor kept the
aerodynamic blading of RM E53I24 and changed the flow passage instead:

- casing diameter increased to 20.86 in. at the stage 1 entrance, decreasing
  linearly to 20.00 in. at the stage 7 entrance (station 7);
- rate of change of hub curvature through stages 1-2 reduced (Fig. 2 only);
- blades of stages 1-6 lengthened by extrapolating twist, thickness and
  camber; base fillets enlarged.

`E55B28_tableI_design_data_modified.csv` is the only table: per stage-entrance
station 1-9, annulus-area ratio A(n-1)/A(n), mean-radius ratio r(n)/r(n-1),
design total-temperature ratio T(n)/T(n-1) and absolute air angle at mean
radius β(n). Area and radius ratios are for the modified passage; the
temperature ratio and air angle are from the original design. The stations
here (1-9 = entrance of stages 1-8 and exit) differ from the RM E53I24
numbering. Fig. 2 of E55B28 (pdf p. 20, printed 19) shows the modified
and original contours: figure only, no dimensions.

The modified-compressor blade lengths, hub/casing coordinates and
extrapolated sections are not tabulated in E55B28 or E55A03.
