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
