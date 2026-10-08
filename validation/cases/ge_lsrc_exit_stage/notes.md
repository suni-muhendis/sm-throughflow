# GE Low Speed Research Compressor, Core Compressor Exit Stage Study

Sources: NASA CR-135391 (Vol. I, blading design), CR-159498 (Vol. II, baseline
Rotor A/Stator A tests), CR-165357 (Vol. IV, Rotor B/Stator B), CR-165358
(Vol. V, Rotor C/Stator B design and tests), CR-165553 (Vol. VI, final
report). Page numbers below are PDF page indices unless "printed" is said.

## Machine and builds

- Four identical stages plus an IGV in the GE LSRC, constant casing diameter
  1.524 m, radius ratio 0.85; the third stage is the test stage (CR-135391
  p12, CR-159498 p17). The axis is vertical, flow enters from the top through
  a bellmouth with a bullet nose. Blade span 11.43 cm, chord about 9 cm.
- Blade counts: 54 rotor blades and 74 stator vanes (labels on CR-159498
  Fig. 3, p42); 53 IGVs (CR-135391 p21). No other counts are printed; the
  solidities in Tables 5-9 are consistent with these counts at the tabulated
  chords (not checked here, interpretation step).
- Stage 7 (AMAC) columns in Tables 2, 3, 5, 6 are the high-speed parent design,
  not an LSRC build.
- Builds tested: Rotor A/Stator A (baseline, CR-159498); screening of Rotor B,
  Stator B, Stator C (Vol. III, CR-159499, not available here); Rotor B/Stator B
  ("best stage", CR-165357); Rotor C/Stator B (CR-165358). Vol. VI p19 also
  reports Rotor A/Stator C (CR-165553 Fig. 13, Table 2).
- Rotor B is identical to Rotor A from the pitchline to the hub (CR-135391
  p22: "Rotor B was identical to Rotor A from the pitchline to the hub region").
  Table 7 nevertheless shows differences from Rotor A at SL6-SL9 in camber
  and stagger (e.g. camber SL7: Rotor A 32.8, Rotor B 31.80; stagger SL6:
  Rotor A 50.36, Rotor B 51.66; Rotor B camber SL7-SL9 = Rotor A SL6-SL8).
  Rotor B's own β1*, β2*, i, δ at SL6-SL11 equal Rotor A's, and β1* - β2*
  gives Rotor A's camber; the printed Camber row of Table 7 is shifted one
  column to the right from SL2 to SL9 (and 35.70 is missing), and the Stagger
  row SL6-SL9 looks shifted the same way. Re-checked in the page image: this
  is a defect of the printed table, not of the transcription. Transcribed as
  printed; the interpretation step should rebuild camber from β1*-β2* (and
  treat Table 7 stagger SL6-SL9 as suspect).
- Stator B is stacked at 30 % chord (CR-135391 p23; CR-165553 p16). The other
  rows' stacking axis is "the usual 50 percent chord location" (same quote).
- Table 4 (Stator B vector diagrams) was computed "as if a new rotor were being
  designed for Stator B" (CR-135391 p15), but the rotor actually kept was
  Rotor A ("new rotor blading was not justified").

## Clearances

- Design (CR-135391 Table 2): rotor tip clearance/blade height 1.35 % for
  Stage A (1.28 % for AMAC Stage 7).
- Tested (CR-159498 p18, repeated CR-165357 p22, CR-165358 p17): average rotor
  tip clearance/blade height 1.36 %, average stator (shrouded) seal clearance
  /blade height 0.78 %. Circumferential-groove casing treatment over rotor 1
  only.
- CR-165358 p19: Rotor C/Stator B tests ran at e/h = 1.53 % (seal 0.78 %),
  "compared to 1.43% for Rotor B".
- CR-165357 p25: an increased-clearance Rotor B/Stator B build at e/h = 2.80 %.
- No absolute clearance in mm is printed; no cold/running distinction.

## Flowpath and axial positions

- Constant-radius annulus: casing r = 76.20 cm, hub r = 64.77 cm (Tables 3, 4
  and the airfoil tables; three tables misprint the hub radius as 67.770, see
  source.json).
- **No axial dimensions are printed anywhere in the reports read.** CR-135391
  Fig. 1 (p35, printed 26) is a layout drawing without dimensions; it only
  labels measurement planes: Plane 0.1 bellmouth flow measurement plane,
  0.5 IGV inlet, 1.0 rotor 1 inlet, 1.5 rotor 1 exit, 2.0 rotor 2 inlet,
  2.5 rotor 2 exit, 3.0 rotor 3 inlet, 3.5 rotor 3 exit, 4.0 rotor 4 inlet,
  4.5 rotor 4 exit, 5.0 compressor exit. CR-159498 Fig. 3 (p42) is an
  undimensioned stage cross section (R_H/R_C = 0.85). Axial gaps would have to
  be scaled from these drawings or taken from other literature (e.g. Wisler
  1985 / later LSRC papers), which is outside this transcription.
- In Fig. 3 the rotor's axial projection is drawn wider at the hub than at
  the tip (figure only, undimensioned).
- CR-135391 Fig. 1 carries a scale note at bottom right that is illegible
  even at 600 dpi (it may read "Scale: one-sixth size", not confirmed); the
  printed reproduction is in any case reduced, so the drawing cannot be
  scaled without a known reference length (the casing diameter 1.524 m could
  serve as one in a later digitizing step).
- Blade axial chord, LE/TE axial positions and inter-row gaps: not printed in
  any of the five volumes (checked text layers for "axial spacing", "gap" and
  the lists of tables/illustrations of all five reports).

## Profiles and conventions

- Rotors: modified circular-arc meanline with double-circular-arc-type
  thickness (CR-135391 p16; CR-159498 p18 says "circular arc thickness
  distributions"). Stators: modified circular-arc meanline with 65-series
  thickness. AMAC Rotor 7: double-circular-arc-type; Stator 7: 65-series on a
  circular-arc meanline (with ΔCAM_TE = -8 deg at the hub of Rotor 7).
- Angles: β1*, β2* are metal angles at LE/TE, measured from the axial
  direction (consistent with the vector-diagram tables, where β' = atan(V'θ/Vz)).
  Tables give "Avg. Radius" (the average of the streamline's LE and TE radii,
  presumably; not stated), chord, solidity, incidence, deviation, camber,
  stagger, t_max/c, t_TE/c, t_max location in % chord. No LE radius or
  LE thickness is tabulated; no axial positions.
- Camber convention differs between tables: Rotor A/Rotor 7/Stator A/Rotor B/
  Rotor C: camber = β1* - β2*. Stator B: camber = β1* - β2* - ΔCAM_LE.
  Stator C: camber = β1* - β2* - ΔCAM_LE - ΔCAM_TE. So "camber" is the
  circular-arc part only for the stators B and C, while for Stator A (ΔCAM_LE
  = 3.50) camber = β1* - β2* includes it. This inconsistency is in the source.
- Rotor C SL1-SL3 have a "Special Airfoil Section" tip meanline (ΔCAM/blend
  given as "*†"); its shape is only in CR-165358 Figs. 15-17 (figure only).
- "Blend" is the chordwise point (% chord) where the over/undercambered region
  joins the circular arc; "-" means no modification at that edge.

## Meanline modification procedure (CR-135391 Section 5, pp. 16-18, printed 7-9)

Verbatim excerpts (read from the page images):

Incidence: "The leading edge meanline angles for AMAC Stage 7 were determined
by utilizing the General Electric Smooth-Flow Incidence Angle Correlation. The
"smooth-flow" incidence angle is defined as the incidence angle in potential
flow through a two-dimensional cascade for which the stagnation streamline
attaches directly to the leading edge point of the airfoil. [...] For the
low-speed stages of this study, incidence angles were selected either to model
the velocity distributions of Stage 7 or to achieve a defined departure from
them".

Deviation: "The deviation angle was obtained by applying a potential flow
cascade analysis (CASC) procedure to establish the required trailing edge metal
angle, rather than the more conventional design method of using Carter's Rule.
[...] it is necessary to determine the potential flow cascade exit air angle,
BCASC, that the blade must be designed to achieve. This angle is different from
the CAFD exit air angle, BCAFD [...] It is the angle obtained after viscous
wakes have been mixed out, after the effects of uncambering due to thick
suction surface boundary layers have been incorporated and after endwall
effects have been included. The difference between these two angles is
expressed as X_p in equation (1).

    X_p ≡ β_CAFD - β_CASC        (1)

This difference, shown in Figure 13 for Stage A, was determined from a detailed
data match/analysis using test data from a previous Low Speed Research
Compressor program [...]"

"The following iterative technique was then used to determine deviation angle:
(1) a trial airfoil trailing edge meanline angle was chosen which established a
trial airfoil shape; (2) a CASC analysis was conducted using the trial airfoil
geometry and the potential flow cascade air angle obtained above; (3) the CASC
solution was examined to determine whether the Kutta condition was satisfied at
the trailing edge; and (4) the above three steps were repeated until the Kutta
condition was satisfied."

Meanline modifications: "These modifications were accomplished by either
overcambering or undercambering the airfoil in the leading edge and/or trailing
edge region. The computer technique used is described as follows for an
airfoil which is to have overcambering in the leading edge region relative to
a circular-arc meanline. Values of input leading and trailing edge meanline
angles are specified together with the amount of leading edge overcambering,
ΔCAMLE, and the blend point along the chord where the overcambered region
blends into the circular arc region. The specified amount of ΔCAM is subtracted
from the input value of leading edge meanline angle to obtain a new "reduced"
value of leading edge meanline angle. A circular-arc distribution of meanline
angle versus percent chord is then constructed between the "reduced" leading
edge meanline angle and the input trailing edge meanline angle. This
circular-arc distribution is modified by blending a cubic curve from the
specified blend point on the circular-arc distribution to the original input
value of leading edge meanline angle, resulting in a meanline that has more
camber in the leading edge region than a circular-arc. Undercamber is
accomplished by simply changing the sign of ΔCAM. Modifications of the trailing
edge region are treated in essentially the same manner. A wide variety of
loading distributions can be achieved by varying the amount of ΔCAM, the blend
point and the location of maximum airfoil thickness."

Only equation (1) is printed; the cubic blend is described in words only (its
end conditions, e.g. slope continuity at the blend point, are not stated). The
"circular-arc distribution of meanline angle versus percent chord" means the
meanline angle varies linearly with chord fraction for a circular arc (in
small-camber terms); the report does not state whether this is linear in angle
or in tan(angle).

(The last two sentences are this transcription's interpretation, not the
report's.)

p19 (printed 10, checked against the page image): "Positive ΔCAM increases the
leading edge metal angle which makes the incidence angle more negative and also
increases suction surface curvature."

All quotes in this section were checked against the page images of pdf
pp. 16-18 (printed 7-9); "[...]" marks omitted sentences.

## IGV

Designed after Dunavant (NACA TN 3959; text cites it as "Reference 5" but the
reference list has it as Reference 7): 53 vanes, pitchline solidity about
1.0, constant chord (value not printed). Design lift coefficient C_Lo and angle
of attack versus immersion are in CR-135391 Fig. 22 (p56) - figure only,
not digitized (C_Lo about 1.1-1.55, α about 13-18 deg). CR-159498 p24: measured
IGV exit swirl "about 0.6° to 1.0° smaller than the design distribution near
the pitch line and about 1.5° to 2.5° smaller near 15% and 80% immersion"
(page image; the "0.6" is blurred, the text layer reads 0.5); "it was decided
to conduct all testing without any changes in stagger angle of the blading."
No IGV geometry table (chord, stagger, camber, profile) exists in CR-135391
or CR-159498; CR-159498 p18 only says "Standard General Electric IGV design
practices were employed" and refers to the design report.

## Figures only (not digitized)

CR-135391: Fig. 1 rig layout (no dimensions), Figs. 3-12 design radial
distributions, Fig. 13 X_p, Figs. 14-34 incidence/deviation, metal angles,
meanline-angle distributions, surface velocities. CR-159498 Fig. 3 stage cross
section. CR-165358 Figs. 12-18 Rotor C angles and tip meanline shape.

## Other volumes

CR-165357 and CR-165553 contain no airfoil geometry tables (checked their
lists of tables: CR-165357 has test plan, preview data, measured vector
diagrams, blade-element performance and a "Design Intent Performance for
Rotor B/Stator B" table; CR-165553 has only Table 1 test plan and Table 2
performance summary). CR-165358 contains the Rotor C design tables (Tables 1,
2), transcribed; its Table 16 is "Design Intent Performance for Rotor A/Stator
A" (performance, not geometry). Measured blade-element data and the
design-intent performance tables were not transcribed (task scope).

## Printed inconsistencies found in the source (all kept as printed)

Found by consistency checks (camber vs β1*, β2*, ΔCAM; i = β1 - β1* and
δ = β2 - β2* against the vector-diagram tables; β' vs atan(Vθ/Vz); U/r) and
each confirmed in the page image:

- Table 3: Rotor Exit β' Pitch SL6 Stg.7 = 46.2 (atan(172.4/178.2) = 44.0);
  Rotor Inlet V'θ SL4 Stg.A = 42.25 (≈45.2 expected); Rotor Exit V'θ SL9
  Stg.A = 29.52 (≈20.52 expected); Rotor Inlet U SL10 = 49.98 (49.90 from U/r).
- Table 4: Stator Exit VZ SL4 printed "25.5" (25.05 would match β = 19.6).
- Table 6 (Stator A): deviation SL5 6.69 and Pitch 6.16 vs 6.96 and 6.60 from
  Table 3; hub radius 67.770 (64.770 elsewhere).
- Table 7 (Rotor B): Camber row shifted one column (SL2-SL9), Stagger SL6-SL9
  apparently shifted; hub radius 67.770.
- Table 8 (Stator B): t_max/c OD "0.90" (0.090); incidence SL8 -7.00 vs -7.40
  from Table 4.
- Table 9 (Stator C): chord SL3 "3.799" (8.799); β1* SL3 54.50 while i and
  camber imply 56.50; t_max/c SL2 0.081 (sequence suggests 0.087); hub radius
  67.770.
- CR-165358 Table 1: Rotor Exit V'θ SL8 = 26.61 (24.61 matches β' = 41.98).
- Table 2 (CR-135391): Stage 7 pressure-rise coefficient 0.638? (last digit
  3 or 8).
- Rotor B nominal tip clearance: 1.36 % (CR-159498 p18, CR-165357 p22) vs
  1.43 % (CR-165358 p19).

## Verification record

All 11 CSVs were read a second time by the first transcriber and a third
time, cell by cell, by a verifying agent on 2026-10-08 from fresh 300-dpi
renders (600 dpi for doubtful cells); no transcription error was found. The
only CSV change was blanking Table 1's row 1, which held supplied headings
("PARAMETER,VALUE") although the table prints none. Cells marked "?":
Table 2 Stage 7 pressure-rise coefficient (0.638?), CR-165358 Table 1 Rotor
Exit β' SL9 (39.77?) and Stator Exit M SL11 (0.084?).
