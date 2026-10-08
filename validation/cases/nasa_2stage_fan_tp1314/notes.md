# NASA TP-1314: 427 m/s two-stage fan, PR 2.40

Source: Cunnan, Stevans, Urasek, NASA TP-1314 (1978), NTRS 19780025166.
PDF page = printed page + 4 for every page used here (e.g. PDF p25 = printed 21,
PDF p84 = printed 80).

## Files

| File | Content | PDF page |
|---|---|---|
| `TP1314_tableI_overall.csv` | Table I (a) fan, (b) stage one, (c) stage two | 24 |
| `TP1314_tableII_{rotor1,stator1,rotor2,stator2}.csv` | Table II design blade-element parameters | 25-28 |
| `TP1314_tableIII_{rotor1,stator1,rotor2,stator2}.csv` | Table III blade geometry | 29-32 |
| `TP1314_tableIV_blockage_blading.csv` | Table IV blockage, aspect ratio, blade counts | 32 |
| `TP1314_fig1_flowpath.csv` | Fig. 1 flow-path coordinate box | 84 |

Table II prints four stacked blocks and Table III three; each blade row's blocks
are merged into one CSV, one line per RP label (TIP, 1-11, HUB). The labels are
the same in every block. Column headings are "<group> <sub-heading>" as
printed. The tables print no units, so row 2 is blank. Units from Appendix C
(PDF p21-22):

- RADII, RI, RO, TI, TM, TO, ZI, ZMC, ZTC, ZO, AERO CHORD: cm
- BETAM, INCIDENCE, DEV, KIC/KTC/KOC, DELTA INC, CONE ANGLE, SETTING ANGLE,
  TOTAL CAMBER, PHISS, STREAMLINE SLOPE: deg
- TEMP: K; PRESS: N/cm2; VEL and SPEED: m/sec; WT FLOW: kg/sec (equivalent);
  RPM: equivalent rpm
- Table I "WT FLOW PER UNIT FRONTAL/ANNULUS AREA": units are not stated
  anywhere (the values match kg/(sec m2)).

## Conventions stated in the report

- **Z** (Fig. 1, ZI/ZMC/ZTC/ZO): axial distance from the rotor-blade-hub
  leading edge, cm (App. A). Rotor-1 hub ZI = 0.000.
- **PERCENT SPAN**: percent of blade span from the tip, referenced to the
  rotor-one outlet (App. C). Text: "Percent span is measured from the tip."
- **Blade elements lie on cones.** KIC/KTC/KOC are angles between the
  blade-element mean camber line on the conical surface and the meridional
  plane at the LE, the transition point and the TE. CONE ANGLE is the angle
  between the axial direction and that conical surface. SETTING ANGLE is the
  aerodynamic chord on the conical surface against the meridional plane.
  TOTAL CAMBER = KIC - KOC.
- Air angle β: between the air velocity and the axial direction; BETAM is the
  meridional air angle. The report gives no explicit sign rule. In the tables
  rotor-relative and stator-inlet angles are positive, absolute inlet angles
  are .0 (no inlet guide vanes), and negative KOC values appear at the rotor-1
  hub and at the stator TEs.
- DELTA INC: mean-camber blade angle minus the suction-surface blade angle at
  the LE. Design incidence: 0 deg to the suction surface for rotors, -3 deg for
  stators (text p7; INCIDENCE SS column).
- TURNING RATIO: ratio of mean-camber-line curvatures ahead of and behind the
  transition point. It is 1.000 for DCA elements (rotor 2 from RP 6 = 42% to
  the hub, both stators); rotor 1 has values other than 1 across the whole span.
- CHOKE MARGIN: the program had an error, so actual choke margins are about
  0.75 percentage point below the Table III values (text p6).
- Standard day 288.2 K / 10.13 N/cm2; Cp 1004 J/(kg K); gamma 1.40 (App. A).

## Profile types

The report says rotor 1 is MCA across the **entire span**, rotor 2 is MCA from
the tip to 44% span and DCA below, and both stators are DCA (PDF p6). The task
brief had "rotor 1 MCA to ~44%, DCA below". That belongs to rotor 2, not
rotor 1. The Table III TURNING RATIO column agrees with the report (see above).

## Fig. 1 flow path

- Read from the native 300-dpi scan. Footnote "a" marks an instrumentation
  survey plane: Z = -2.347 (station 1), 18.659 (station 2, between stator 1
  and rotor 2), 36.706 (station 3, behind stator 2).
- Some outer-radius cells hold only a downward arrow: the value above carries
  down (24.384 from Z=10.160 to 18.659; 23.622 from Z=27.940 to 40.640). They
  are written as "↓" in the CSV, as printed, and left for interpretation.
- These values agree with the Table III TIP radii: rotor-1 tip RI 25.400 lies
  between the casing points, stator-1 tip 24.384 = casing 24.384, stator-2 tip
  23.622 = casing 23.622, and rotor-1 hub RI 10.160 at Z=0 = inner 10.160.
- **This flow path is also used by NASA TP-1493**, the low-aspect-ratio
  first-rotor version of the same fan. There the rotor-1 LE/TE moved but the
  flow path stayed the same (as stated in the task brief; not checked against
  TP-1493 in this step).

## Plausibility checks (not used to change values)

All Table II rows: |V| = sqrt(Vm^2+Vt^2) and |W| from (U - Vt) within 0.1 m/s.
ABS/REL BETAM agree with the velocities. Mach ratios agree with velocity ratios.
MERID VEL R = Vm_out/Vm_in. U/r = 16.80 (= 16042.8 rpm) for both rotors.
Table III RI/RO equal Table II RADII IN/OUT exactly. KIC-KOC equals TOTAL
CAMBER. Incidence and deviation from Table II minus Table III blade angles
agree within 0.1 deg (0.3-0.4 deg at the rotor hubs, probably the
cone-angle-based angle correction). No printed value failed a check.

## Uncertain cells ('?')

| File | Row | Column | Value | Reason |
|---|---|---|---|---|
| tableII_rotor1 | 11 | RADII OUT | 12.173? | digit dropout; Table III RO prints 12.173 |
| tableII_stator1 | 1 | RADII OUT | 23.761? | last digit faint; Table III RO 23.761 |
| tableII_stator1 | TIP | LOSS COEFF PROF | .094? | middle digit damaged |
| tableII_rotor2 | 6 | WHEEL SPEED OUT | 329.9? | middle digit faint; U/r agrees |
| tableII_rotor2 | 10 | WHEEL SPEED IN | 244.2? | leading digits damaged; U/r agrees |
| tableII_stator2 | TIP | MERID VEL IN | 168.8? | last digit damaged |
| tableII_stator2 | 1 | ABS VEL OUT | 170.3? | middle digit damaged |
| tableII_stator2 | 2 | REL VEL OUT | 170.3? | middle digit damaged |
| tableII_stator2 | 3 | MERID VEL IN | 174.5? | last digit damaged |
| tableIII_rotor1 | 1 | BLADE ANGLES KOC | 58.37? | 3/8 ambiguous; camber and deviation favour 58 |
| tableIII_rotor1 | 3 | TOTAL CAMBER | 5.99? | middle digits damaged; KIC-KOC = 5.99 |
| tableIII_rotor2 | 1 | BLADE ANGLES KTC | 57.70? | printed "57 70" with a damaged 7 and decimal point |
| tableIII_rotor2 | 9 | RADII RI | 15.652? | last digit damaged; Table II 15.652 |
| tableIII_rotor2 | 10 | RADII RI | 14.537? | last digit damaged; Table II 14.537 |

## Figure only / not transcribed

- Fig. 1 sketch (blade-row outlines); Fig. 2 photograph; Fig. 3 (diffusion
  factor/loss correlations); Fig. 4 (shock-loss parameter); Fig. 5 (Campbell
  diagrams); Figs. 7-8 (probe and circumferential probe locations).
- Tables V-VII (overall performance at 100/80/60% speed) and VIII onwards
  (measured blade-element performance) are test data. They are outside this
  geometry step and were not transcribed.

## Pass-B resolution of uncertain cells

Second targeted pass over every cell that carried '?'. Each cell was re-read from a 600-dpi render of its page (crops zoomed further where needed), independently of the earlier value, and checked against an independent relation where one exists. Rules: clear reading that agrees with the check -> written without '?'; clear print that disagrees with the check -> printed value kept without '?' and listed under print errors; otherwise '?' kept. Row = line number in the CSV (line 1 = headings, line 2 = units).

Resolved 14, still '?' 0, print errors 0.

| File | Row | Column | Old | New | Check | Reason |
|---|---|---|---|---|---|---|
| TP1314_tableIII_rotor1.csv | 4 | BLADE ANGLES KOC | `58.37?` | `58.37` | TOTAL CAMBER = KIC - KOC: 64.50 - 58.37 = 6.13 (printed 6.13); 53.37 would also break the KOC trend 59.36, -, 57.16 | 600-dpi zoom: second digit is an 8 with its left side dropped out (looks like 3); exact relation decides 8 |
| TP1314_tableIII_rotor1.csv | 6 | TOTAL CAMBER | `5.99?` | `5.99` | TOTAL CAMBER = KIC - KOC = 60.02 - 54.03 = 5.99 | 600-dpi zoom: 5 and final 9 legible, first decimal digit dropped out; exact relation fixes 5.99 |
| TP1314_tableIII_rotor2.csv | 4 | BLADE ANGLES KTC | `57.70?` | `57.70` | no exact relation for KTC; monotone radial trend 58.37, 57.70, 56.96 (KIC and KOC fall the same way) | 600-dpi zoom: reads 57 70 with a broken 7 and the decimal point missing; trend agrees |
| TP1314_tableIII_rotor2.csv | 12 | RADII RI | `15.652?` | `15.652` | Table II rotor 2 RADII IN row 9 = 15.652 | 600-dpi zoom: last digit broken (7-like) but Table II = Table III radii fixes 2 |
| TP1314_tableIII_rotor2.csv | 13 | RADII RI | `14.537?` | `14.537` | Table II rotor 2 RADII IN row 10 = 14.537 | 600-dpi zoom: 14.53 legible, last digit broken; Table II fixes 7 |
| TP1314_tableII_rotor1.csv | 14 | RADII OUT | `12.173?` | `12.173` | Table III rotor 1 RO row 11 = 12.173; U_out/U_in x r_in = 204.5/184.4 x 10.973 = 12.169 | 600-dpi read: second 1 broken (12.i73); checks agree |
| TP1314_tableII_rotor2.csv | 9 | WHEEL SPEED OUT | `329.9?` | `329.9` | U = omega r: 330.1 x 19.636/19.646 = 329.93 | 600-dpi read: 9 with broken loop; relation agrees |
| TP1314_tableII_rotor2.csv | 13 | WHEEL SPEED IN | `244.2?` | `244.2` | U = omega r: 405.3 x 14.537/24.127 = 244.2 | 600-dpi read: hundreds and tens glyphs broken, .2 clear; relation fixes 244.2 |
| TP1314_tableII_stator1.csv | 3 | LOSS COEFF PROF | `.094?` | `.094` | stator PROF = TOT on every row (TOT .094; LOSS PARAM PROF = TOT .037 on the same row) | 600-dpi read: middle digit broken (.0?4); relation fixes .094 |
| TP1314_tableII_stator1.csv | 4 | RADII OUT | `23.761?` | `23.761` | Table III stator 1 RO row 1 = 23.761 | 600-dpi read: last two digits broken (23.7??); Table III fixes 23.761 |
| TP1314_tableII_stator2.csv | 3 | MERID VEL IN | `168.8?` | `168.8` | VM = sqrt(V^2 - VTH^2) = sqrt(217.8^2 - 137.7^2) = 168.75 | 600-dpi read: 168. clear, tenths broken; relation agrees |
| TP1314_tableII_stator2.csv | 4 | ABS VEL OUT | `170.3?` | `170.3` | stator: ABS VEL OUT = REL VEL OUT = MERID VEL OUT = 170.3 (TANG VEL OUT .0) | 600-dpi read: middle digit broken (17?.3); relation fixes 170.3 |
| TP1314_tableII_stator2.csv | 5 | REL VEL OUT | `170.3?` | `170.3` | stator: REL VEL OUT = ABS VEL OUT = MERID VEL OUT = 170.3 | 600-dpi read: 17?.3 broken; relation fixes 170.3 |
| TP1314_tableII_stator2.csv | 6 | MERID VEL IN | `174.5?` | `174.5` | VM = sqrt(222.1^2 - 137.4^2) = 174.50 | 600-dpi read: 174. clear, tenths broken; relation fixes 174.5 |
