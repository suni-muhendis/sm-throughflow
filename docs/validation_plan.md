# Validation plan: consistency against measurement

Status: draft for discussion (2026-10-15). Nothing here has been run beyond
the first Stage 35 comparison described in the last section.

## Goal

A throughflow model with empirical correlations will not reproduce every
compressor exactly. The environment does not need it to. It scores designs
against each other, so what it needs is an error that is **consistent**: the
model's departure from measurement should be about the same from one design
to the next. If one machine comes out at +3 % pressure rise and -5 % mass
flow, another should come out near +2.8 % and -5.2 %, not -1 % and +4 %. A
consistent model ranks designs correctly and gets the differences between
them right, which is what a designer and the score rely on.

Validation therefore measures the **spread** of the error across cases (and
across operating points of one case), not its mean. A mean offset is
recorded and may stay. A spread that depends on the design is what must be
found and removed.

This holds at two levels, both part of the gate:

- **Global** quantities: pressure ratio, mass flow, efficiency, stall margin.
- **Spanwise** profiles: how work, pressure, flow angle and loss are
  distributed from hub to tip.

## 1. What is compared

### Level 1: overall performance at characteristic anchors

Comparing two characteristics "at the same mass flow" is unstable near
choke, where a small shift in flow changes the pressure ratio a lot. Each
speed line is therefore reduced to anchors that mean the same thing on every
machine:

| Anchor | Quantities |
|---|---|
| Choke | Maximum mass flow at the speed, where the measured characteristic is vertical (the relative fall of PR - 1 between the two highest-flow points is at least 10 times their relative flow difference). Elsewhere the highest measured flow is a rig limit, not a choke point, and is not compared. |
| Peak efficiency | Peak efficiency, and mass flow and pressure ratio at that point. |
| Near stall | Mass flow, pressure ratio and efficiency at the last stable point; stall margin. |
| Every measured point | PR, TR and efficiency at the measured mass flow (secondary). |

The stall anchor compares the model's stall criterion (W_RE, Aungier 9-16 to
9-19) with the measured last stable point, as the flow at which the model's
minimum stall margin crosses zero.

### Level 2: stage-exit profiles (what a designer uses)

These are the radial profiles a designer reads and passes to the next row:

- total pressure and total temperature;
- absolute flow angle;
- meridional velocity.

They are compared where they were measured, normally downstream of each
stator. In the NASA Lewis single stages, the rotor-exit ("station 2") values
are not measured; they are translated from station 3 along design
streamlines, so they rank below station 3.

### Level 3: blade-element quantities (to explain errors)

For every row at every measured span:

- incidence and deviation;
- loss coefficient, with the shock and profile parts where the report
  separates them;
- D-factor;
- the row's total-pressure and total-temperature ratios.

These do not gate on their own. They locate the correlation responsible for
a Level 1 or Level 2 error.

## 2. Error metrics

Errors are taken in forms that compare fairly between a 1.2 and a 2.0
pressure-ratio machine:

| Quantity | Error |
|---|---|
| Pressure ratio | Relative error in pressure rise: (PR_model - 1)/(PR_meas - 1) - 1. |
| Temperature ratio (work) | (TR_model - 1)/(TR_meas - 1) - 1. |
| Mass flow (choke, peak, stall) | m_model/m_meas - 1. |
| Efficiency | Difference in points. |
| Stall margin | Difference in points. |
| Angles, incidence, deviation | Difference in degrees. |
| Loss coefficient | Difference. |

Every model quantity is computed with the report's own averaging. For
example, the Lewis reports mass-average T0, energy-average P0 (a
mass-averaged isentropic temperature ratio), and define stage efficiency with
the station-2 temperature ratio (TP-1338 Appendix B).

### Spanwise profiles: level and shape

A profile error e(s), model minus measurement at span s, mixes two things.
Its mass average is the level, which the global comparison already covers.
The rest, e(s) minus its mean, is the shape. The shape error is compared in
normalized form so that machines of different loading line up:

- P0 shape: (P0(s) - P0_avg)/(P0_avg - P0_in);
- T0 shape: (T0(s) - T0_avg)/(T0_avg - T0_in);
- Angle, deviation and loss: absolute values, since they are already
  comparable.

Profiles are compared at the reports' measured spans, interpolated to a
common set (5, 10, 15, 30, 50, 70, 85, 90 and 95 percent span from the tip,
the Lewis grid) in two zones:

- **Core**, 15 to 85 percent span, where the correlations apply.
- **End-wall**, 5 to 15 and 85 to 95 percent span, where clearance flows,
  end-wall boundary layers and secondary flows dominate. This zone is
  reported separately, with looser tolerances.

### Consistency statistics

For each quantity q, the errors e_k over the cases k give:

- the bias, mean(e_k), which is recorded and not gated;
- the **spread, std(e_k), which is gated**;
- for profiles, the spread at every span of the shape error, and its RMS over
  each zone.

**Family deltas.** For pairs of cases from one rig, the change between them
as measured is compared with the change the model gives:
(model_B - model_A) - (meas_B - meas_A). This is the most direct test of the
goal, since bias, rig and instrumentation cancel. Families in `validation/`:

- Stages 35, 36, 37 and 38: one flow path and rig, different loading and
  aspect ratio.
- Rotor 37 alone against Stage 37: the same rotor with and without its
  stator.
- Stage 8E with its tip-clearance variants: one stage, different clearance.
- Rotor 67 against the two-stage fan built around it.
- The four NASA stages 12-5, 14-10, 16-11 and 18-13, and stages 52, 53 and
  55, as they turn out to share rigs.

**Across operating points.** The same statistics are taken along one speed
line. An efficiency error of -8.6 points at peak efficiency and +0.5 at near
stall (Stage 35, simulator v5) is an inconsistency, even though both points
belong to one machine.

## 3. Proposed tolerances (to be agreed)

These numbers are a starting point. They are set on the spread, not the bias,
and will be revisited once the first family has run.

| Quantity | Spread target |
|---|---|
| Pressure rise | 2 % |
| Work (TR - 1) | 2 % |
| Choke mass flow | 1 % |
| Peak-efficiency mass flow | 1.5 % |
| Peak efficiency | 1.5 points |
| Stall-point mass flow | 3 % |
| Core P0 and T0 shape (RMS) | 0.05 |
| Core exit angle and deviation | 1.5 deg |
| Core loss coefficient | 0.02 |
| End-wall zone | reported, about twice the core values |

## 4. Rules that keep the result honest

1. **Physics changes follow sources, not fits.** A change must be justified by
   the correlation's source or by a geometric fact, like the computed throat
   or the shock expansion angle. A constant is never tuned to make one case
   agree. Every change reruns every case, and moves the simulator version
   once tagged.
2. **Development and holdout.** Cases used to diagnose the model form the
   development set. The holdout set is not looked at until the physics is
   frozen. Proposed split:
   - Development: Stages 35 to 38, Rotor 37, stages 52, 53 and 55, Stage 8E,
     GE LSRC.
   - Holdout: the NACA multistage machines, E3 HPC, 74A, the P&W fan and exit
     stage, LSAC, UTRC.
3. **Missing inputs follow one rule for every case.** When a report does not
   give a tip clearance, an axial position or a stator configuration, the same
   documented rule applies to every case. Each such input is varied over a
   plausible band (for example clearance x0.5 and x1.5), and an error inside
   that band is not attributed to the model.
4. **Measurement uncertainty and data quality are recorded.** This covers
   uncertainties the reports state, translated stations, and doubtful cells.
5. **Coverage.** The cases must span what the design rules allow: subsonic
   and transonic, low and high loading, aspect ratio, solidity, one stage and
   several. Consistency is claimed only where it was tested; it is the
   region a scored design may enter.

## 5. Decisions and open points

Decided (2026-10-15):

- **Tolerances.** The values in section 3 are adopted. They will be revisited
  after the first family has run.
- **Matched-point comparison.** Spanwise profiles are compared at the
  measured mass flow and also at a matched normalized flow, m/m_choke (on
  speed lines whose measured choke flow is known). This
  separates profile-shape errors from choke-flow errors.
- **Inlet profile.** The task contract is not changed for now.
  - Each case sets the end-wall model's inlet state (blockage and shape
    factor) from the measured inlet profile, by one fixed rule for every case.
  - The Lewis single stages have nearly uniform inlets. In Stage 35 the
    deficit is 2.2 percent of P0 at 5 percent span from the tip and under
    0.3 percent elsewhere, so the rule suffices there.
  - An optional, task-owned inlet profile will be added when a case with a
    strong inlet profile shows the rule is not enough. Candidates are an
    embedded stage (GE LSRC, P&W exit stage) and multistage middle sections.
    It would also allow design tasks posed behind an upstream component.

Open:

- **Unmeasured spans.** The hub and tip rows (0 and 100 percent span) are not
  measured in Tables V and VI. Compare only at measured spans; never
  extrapolate the measurement.
- **Multistage cases.** Interstage data give stage-by-stage errors. Their
  growth through the machine is a consistency measure of its own.

## 6. Work plan

1. **Framework.** `validation/run.py`:
   - case adapters per report format (NASA Lewis first; NACA, GE and P&W
     later), model quantities with each report's averaging;
   - anchors, Levels 1 to 3, per-case results under `validation/results/`;
   - a consistency report (`validation/reports/consistency.md`) with tables
     and plots of bias, spread and family deltas.

   Built and checked on Stage 35.
2. **Known geometric fix (done).** The suction-surface expansion angle of
   the shock model is read off the constructed section for
   double-circular-arc rows, which removes Aungier's circular-arc
   assumption. On Stage 35 the peak-efficiency error fell from -8.0 to -5.1
   points, and the rotor's core loss bias from 0.063 to 0.032. With the
   printed PHISS angles the peak efficiency would be 0.814 (measured 0.845):
   one a/c per row cannot reproduce the nearly straight front of the MCA tip
   sections.
3. **First family.** Transcribe the measured Tables IV to VI of Stages 36, 37
   and 38 and the Rotor 37 data. Run the four stages, and produce the
   consistency statistics and family deltas.
4. **Diagnose.** Rank the error sources by the spread they cause, and fix them
   one at a time under rule 1, rerunning everything after each fix.
5. **Widen the development set.**
   - Stages 52, 53 and 55, and 8E (the clearance deltas test the clearance
     model directly).
   - GE LSRC (low speed, subsonic).
   - Extend Stage 35 to its part-speed lines.
6. **Freeze and holdout.** Tag the simulator, run the holdout set once, and
   publish the statistics.
7. **Score gate.** Open the score when the frozen model meets the spread
   targets on both sets, within the region the cases cover; the design rules
   may be narrowed to that region.

## Results so far: stages 35 to 38 (development set)

`python validation/run.py` runs them (the report is
`validation/reports/consistency.md`). The four stages share one rig and flow
path; their measured overall performance (all speeds) and blade-element data
(100 percent speed; Stage 35 also 90 and 70 percent) are transcribed.

**Stage 35 alone (first run).**
- Work was right: stage TR within 0.006 at five of six design-speed points.
- Loss was too high and too flat: peak efficiency 8.6 points low, near-stall
  efficiency 0.5 points high.
- The main cause was the shock model's circular-arc expansion angle,
  10 to 17 deg against the printed 1.5 to 11 deg.

**The family, step by step.** Each row gives the 100 percent speed errors
for stages 35 / 36 / 37 / 38.

| Physics | Choke flow | Peak efficiency (points) |
|---|---|---|
| Book expansion angle, MCA as parabolic arc | +2.0 / not run / not run / not run | -8.0 / not run / not run / not run |
| Geometric expansion angle, MCA as parabolic arc | +3.4 / -6.7 / +3.9 / fails | -5.1 / unreachable / -4.0 / fails |
| Geometric expansion angle, MCA sections | +3.1 / +3.7 / +4.8 / +0.2 | -3.6 / -0.3 / -2.0 / -0.1 |

Choke flow in percent. The family was first run with the geometric
expansion angle in place.

How the MCA sections fixed it. As parabolic arcs, the rotors took Howell's
deviation rule and underturned too little: rotor deviation was 1.7 deg low in
the core and 2.8 deg low at the walls. The resulting overturning had three
effects:
- too much work;
- 4.7 deg too much stator incidence;
- D_eq above Aungier's wake-blockage threshold on the highly loaded
  stages 36 and 38. There the hub wake blockage fed on itself, and the model
  choked 7 percent early (Stage 36) or its radial equilibrium collapsed
  (Stage 38).

With the MCA sections (Lieblein's circular-arc deviation, the true
meanline), all four stages run and the design-speed errors share their sign.
The MCA rows have since taken the Lewis design code's Carter rule for their
design deviation (`docs/compressor_correlations.md`): lower pressure-rise
error and spread, but Stage 38's design-speed choke moves from +0.2 to -2.0
percent. The consistency report reflects the current model.

**Open, in order of the spread they cause:**
1. **Work rises as speed falls.** At the measured flow, the stage
   pressure-rise error is +3 to +10 percent at design speed, +14 to +21
   percent at 90 percent and +29 to +36 percent at 70 percent. At the same
   flow and speed, the rotor turns the flow too much at part speed: its
   deviation is 2.7 deg low at 70 percent on Stage 35. The off-design
   deviation (6-76, 6-77) is the first suspect.
2. **Rotor-inlet incidence is +1.6 deg on every case** (spread 0.6 deg). The
   reports' edge values carry their designers' blockage, so this is a
   consistent offset, not a target.
3. **No model stall point** is found above 75 percent of choke flow on any
   speed line. The stall criterion (9-16 to 9-19) is not yet tested.
4. Stage 36 fails to converge at its two lowest design-speed flows.

## Results so far: stages 52 and 53 (fans)

Two 1.6-pressure-ratio fan stages from TM X-3083 and TP-1299, double-circular-
arc rotors and stators, measured on one rig (overall performance at all
speeds, blade-element data at 100 percent). The adapter and its assumptions
for what the reports leave out (clearance, station planes, Stage 52's 2-chord
stator position) are listed per case in the consistency report.

**Start-up failures were numerical.** From the cold start, Stage 53 gave no
point at 100 percent speed and Stage 52 lost its high-flow points: on the
first outer iterations a stator hub stream tube with low exit velocity drove
its D_eq-based loss up until the quasi-normal had no solution. The same points
converge from a neighbouring solution. The solver's start-up homotopy
(`docs/throughflow_solver.md`) recovers 17 measured points without moving any
point that converged cold.

**Spanwise mixing does not change this.** Gallimore's model at the level of
his eq. (9) moves the stage values by a few parts in a thousand on these single
stages; it stays off (`docs/throughflow_solver.md`).

**Near-wall blade elements are outside the model.** Aungier applies the
free-stream conditions inside the end-wall boundary layers and corrects only
the mass balance through the displacement blockage (p. 53 and chapter 8), so
the stream surfaces next to the walls carry core-flow velocities and
incidences. The measurements at 5 and 10 percent span from either wall lie
inside the boundary layers. At the Stage 53 stator inlet (behind a 20 cm
duct) the measured hub meridional velocity at 5 percent span is about 25
percent below the model's (160 against 207 m/s at reading 2996), so the
model's stator hub incidence is 5 to 7 deg more negative than measured and
Aungier's negative-stall loss raises the hub entropy until, at the lowest
flows, the stator exit has no solution. The model's own end-wall analysis puts
the hub boundary layer at 14 mm there (10 percent of span), and its power-law
profile accounts for only about 10 percent of the velocity defect at 5
percent span. Rule: blade-element comparisons are judged in the core zone
(15 to 85 percent span from the tip); the end-wall zone is reported but
explains rather than gates, and Stage 53's remaining failures at 100 and 120
percent speed are recorded as this limit, not tuned away.

**Open, from the 100 percent speed blade elements:**
1. **Stator 53 turns less than designed.** Its measured deviation is 2.5 to
   4.5 deg above the model's in the core (8.5 to 9.5 deg against 4.7 to 6
   deg at reading 2996), but the model is within 0.5 to 1 deg of the
   designer's own design deviation (5.2 to 6.7 deg, TP-1299 Table III), and
   the report states that "at all span locations, the measured deviation
   angles were significantly greater than design values", with a missing
   hub wake that indicates separation and a radial shift through the stator
   (TP-1299, "Radial Distributions" and "Variations with Incidence Angle"). Stator 52, of the same family, is within 1 deg in
   the core. This is a stator that missed its design, which no cascade
   correlation predicts; it is recorded, not corrected.
2. **The stage-exit total-temperature profile is too flat** on all six
   cases (stages 35-38, 52, 53): the shape error is -0.04 to -0.08 near the
   tip and +0.02 to +0.07 near the hub, with the same sign on every case.
3. **Part-speed work: the off-design deviation is linear by choice.** At 70
   percent speed the rotors run 4 to 6 deg above their reference incidence.
   Measured rotor deviation there is as high as at design speed or higher
   (Stage 35, 5 percent span: 6.2 against 5.6 deg); the model's falls (4.7 to
   2.6 deg), because (6-77) adds only 0.03 to 0.08 deg per degree of incidence
   (6-76) while its axial-velocity-ratio term removes about 1.5 deg. Lieblein
   (NASA SP-36, ch. VI, "Variation with incidence angle") gives the slope
   only at reference incidence, for "the region of minimum loss", which "is
   generally small". Aungier (pp. 143-144) notes that in cascades the slope
   approaches unity at positive stall, tried Novak's (1973) incidence-
   dependent form "in several unsuccessful attempts", and kept the linear
   model as "somewhat arbitrary" but better in practice. Wilson, Mani and
   Acosta's contraction effect in place of the 10 (1 - W_m2/W_m1) term
   lowered the pressure-rise spread (0.104 to 0.089 over 92 points) only by
   worsening the design-speed MCA stages (+2 to +11 percent), so the book's
   term stays. Open: whether an incidence-dependent slope is worth testing
   against Aungier's advice.

## Results so far: stage 55 (low-pressure-ratio fan)

TM X-3101, a 1.20-pressure-ratio Hamilton Standard fan on the same rig:
double-circular-arc rotor, stator of "NACA 400 Series airfoils" that the
report does not define further. The adapter represents the stator by the
contract's nearest family, C.4 thickness on a parabolic arc with maximum
camber at 0.37 chord (Table V's (ZMC - ZI)/(ZO - ZI)), and takes the flow
path from Fig. 1 outside the blade rows but the tables' three-decimal edge
radii over them (the figure's two-decimal hub differs by up to 0.4 cm at the
stator). All 20 measured points converge from the cold start. The stage
pressure-rise error is +10 to +13 percent at every speed from 80 to 120
percent and the stage efficiency within -2.3 to +3.0 points: the most
uniform case so far, though its stator section is an assumption.

## Results so far: stage 8E at four tip clearances

TP-2049 tested one stage (rotor 8E, stator 8, multiple circular arcs) with
the casing cut back to four nominal nonrotating tip clearances, 0.061, 0.102,
0.140 and 0.178 cm; the report's calculated growth of 0.040 cm gives running
clearances of 0.021 to 0.138 cm (0.2 to 1.1 percent of the leading-edge
blade height). Table VI was transcribed for all four (100 and 70 percent
speed); the tables print X FACTOR instead of the turning-rate ratio, so C1/C2
and the transition point follow from the printed KTC and ZTC.

**The model barely feels the clearance.** At equal flow (28.9 kg/s, design
speed), going from the smallest to the largest clearance:

| | Measured | Model |
|---|---|---|
| Stage efficiency | -6.7 points | -0.6 points |
| Stage pressure rise (PR - 1) | -20 percent | -1 percent |
| Rotor temperature rise (work) | -10 percent | none |

Aungier's clearance model (6-85 to 6-89) adds a loss and spreads it
linearly over the span; it has no effect on the turning, so the rotor's
work does not change. The measurements show the clearance removing work as
well as adding loss. At the measured points the stage pressure-rise error
therefore grows with clearance (peak efficiency: +5, +17, +20, +24 percent
at design speed), the largest single source of spread found so far.

Two published clearance models were read and neither reaches this size:
- Roberts, Serovy and Sandercock (J. Eng. Gas Turbines Power 108, 1986,
  131-137) add a rotor deviation of 2.7e4 (delta*_t/h)(TC/h) deg at 5
  percent span from the tip (eq. 4), with fixed shapes towards midspan and
  the hub (eqs. 5-8); fitted to subsonic middle stages at design point. For
  8E (delta*/h about 0.004) it gives roughly 0.2 to 1.2 deg over the outer
  tenth of the span, about 1 percent of the rotor work.
- Gallimore (J. Turbomach. 120, 1998, 662-670) limits the tangential blade
  pressure force near the walls, zero in the gap and constant over ten
  clearances; on his low-speed rotor, clearance from 1.2 to 3.0 percent of
  chord cost 0.5 points of efficiency (0.7 measured).
Stage 8E is transonic (tip speed 423 m/s), where the clearance flow's
blockage, not its turning alone, is the likely mechanism; no model of it is
in hand. Recorded as a limit, to return to with a transonic clearance data
set (none is in the case list yet).

Solver fix found on the way: the end-wall boundary layer's (8-23) divided by
zero when a very thin profile rounded H1 to 1; the outer thickness is now
taken as given there (no change elsewhere beyond round-off, 7e-11).

## Results so far: the earlier Lewis transonic stages (8-8, 12-5, 14-10, 16-11, 6-1)

Five more single stages of the rig of stage 8E-8, multiple-circular-arc
blading designed in 1970-1973 (TM X-2926, X-2658, X-2645, X-2904, X-2731):
Table VI transcribed at 100, 90, 80 and 70 percent speed (8-8 also 60 and
50); the geometry tables are printed in column parts and joined on RP.
Stages 12-5, 8-8 and 14-10 form a solidity series (rotor tip solidity 1.7,
1.5 and 1.3). Rules: running clearance = cold clearance less the TP-2049
growth of 0.040 cm (12-5 states none and takes the family's 0.05 cm); design
speed from the design tip speed; inlet blockage 0.02 (no blade elements).

Mean errors at the measured flow (stage PR - 1 / stage efficiency points):

| Stage | 100 % | 90 % | 70 % |
|---|---|---|---|
| 8-8 | -18 % / -4.5 | -6 % / +0.8 | +22 % / +10.1 |
| 12-5 | -2 % / +2.6 | +8 % / +7.5 | +22 % / +10.3 |
| 14-10 | -9 % / +0.7 | +2 % / +4.5 | +22 % / +11.1 |
| 16-11 | -16 % / -4.8 | -2 % / -1.3 | +12 % / +2.9 |
| 6-1 | +1 % / +1.2 | +8 % / +3.9 | +23 % / +7.1 |

The part-speed pattern of stages 35-38 repeats with the same size (+22
percent pressure rise at 70 percent speed on four of five stages), and here
the stage efficiency is also 7 to 11 points too high at 70 percent: the
measured stage efficiencies there (0.72 to 0.82) fall well below the rotor's,
so the stators lose far more at the high incidence of part speed than
Aungier's off-design loss gives. Over all 210 points the stage
pressure-rise error is +7.2 percent (spread 12.8) and the stage efficiency
error +1.6 points (spread 5.5).

## Off-design deviation: Creveling and Carmody's increment, tried and not adopted

The part-speed excess work comes mainly from the rotor deviation. Stage 35 is
the only case with blade elements at 70 percent speed. On its core span (15
to 85 percent), the model's rotor deviation there is 0.7 to 4 deg low, while
the core rotor incidence is 1.2 deg high at every speed. A uniform extra 1
deg of rotor deviation lowers the rotor work by about 9 percent at 70
percent speed and 7 percent at design speed, so a small speed-dependent
deviation error is enough to explain the trend. At 70 percent speed the
rotor runs 4 to 6 deg above Aungier's design incidence. His linear slope
(6-76) adds only 0.3 deg there; it is the reference slope of Lieblein's
low-speed cascade data.

Sources on off-design deviation of transonic rows, all read:

- H. F. Creveling and R. H. Carmody, *Axial Flow Compressor Computer
  Program for Calculating Off-Design Performance (Program IV)*, NASA
  CR-72427, Allison EDR-5898, August 1968. Later citations often print the
  number as CR-72472; the cover reads CR-72427. The program adds an increment
  to the reference deviation, correlated from NASA rotor and stator data at
  inlet Mach numbers 0.5 to 1.1:
  `delta - delta_ref = eps_ref f((i - i_ref)/eps_ref)`, where `eps_ref` is
  the reference air turning (eq. 2, 3; figs. 5 to 7). The table `f` is in
  function DEVI of the source deck (p. B-14), and its call is on p. B-58.
  Near the reference incidence, `f` has a slope of about 0.5, not Aungier's
  0.03 to 0.08.
- J. E. Cahill, *Identification and Evaluation of Loss and Deviation Models
  for use in Transonic Compressor Stage Performance Prediction*, M.S. thesis,
  Virginia Polytechnic Institute and State University, 1997. He compared the
  shapes of the off-design deviation curves, each shifted onto the measured
  minimum-loss point, with rotor 35 data at 70, 90 and 100 percent speed.
  RMS errors: Hearsey 0.5 to 1.4 deg; Creveling 1.6 to 2.7 deg; Lieblein
  with the Jansen and Moffatt conversion 6.7 to 18.5 deg; Howell 2.5 to
  9.8 deg (Table 4.8).
- K. M. Boyer, *An Improved Streamline Curvature Approach for Off-Design
  Analysis of Transonic Compression Systems*, Ph.D. dissertation, Virginia
  Polytechnic Institute and State University, 2001 (section 3.2). His SLC
  code uses Hearsey's four-piece curve for deviation against incidence, and
  still needed a user-set extra deviation at every operating point. He
  calls a detailed assessment of off-design deviation for highly transonic
  blading "needed".
- Hearsey's method, the best in Cahill's test, is documented only in Boeing
  reports that Boyer and Cahill cite: *Program HT0300 NASA 1994 Version*,
  D6-81569TN, and an HT0300 report of 1970. Neither is openly available.
  AGARD-R-745 (Çetin, Üçer, Hirsch and Serovy, 1987), the review that
  recommends Creveling's correlation, could not be downloaded from DTIC.

The trial replaced the linear incidence term of (6-77) with Creveling's
increment, about Aungier's design incidence and deviation. The term in
`W_m2/W_m1` was kept. Results at the measured flow, on the 202 points where
both models converge (mean / spread):

| Error | Aungier (6-77) | Creveling |
|---|---|---|
| Stage PR - 1 | +7.7 % / 12.3 % | -0.3 % / 12.4 % |
| Stage efficiency | +1.7 / 5.2 points | +1.0 / 5.6 points |
| Rotor TR - 1 | +3.0 % / 8.1 % | -3.0 % / 8.2 % |
| Stage PR - 1 at 100 / 90 / 80 / 70 % speed | -0.8 / +2.2 / +7.0 / +20.1 % | -8.6 / -4.9 / -1.1 / +10.9 % |

Creveling's increment moves the level at every speed. It narrows the gap
between 100 and 70 percent speed only slightly, from 21 to 20 points, and
leaves the spread unchanged. On stage 35 it brings the stator deviation
within 1 deg of the data. The core rotor deviation becomes 2 deg too high at
90 and 100 percent speed and 0.5 to 1.3 deg too high at 70 percent, partly
because the 1.2 deg excess incidence is now multiplied by a slope of 0.5.
Since the aim is a consistent error, not a small one, the model keeps
Aungier's (6-77), and Creveling's increment is not in the code. The speed
dependence of transonic rotor deviation stays open; the sources above
expect it.
