"""Map a NASA Lewis single-stage case (Table III blade geometry, Fig. 1 flow path) to the v2 contracts.

The transcribed tables stay verbatim; every interpretation lives here and is
listed in ``ASSUMPTIONS`` so a run can report it:

- Sections. Each printed blade element lies on a cone through (ZI, RI) and
  (ZO, RO). Its span fraction is taken at each edge from the edge radii of the
  HUB and TIP rows and the values are interpolated onto the contract's eleven
  span fractions: KIC at the leading edge, KOC at the trailing edge, chord and
  thickness at the mean of the two.
- Angles. KIC and KOC are measured on the element's cone, from the meridional
  direction; the contract takes angles in the axial-tangential plane, which
  the solver projects with tan(k_m) = cos(phi) tan(k) (Aungier 9-4, 9-5).
  The inverse is k = atan(tan(KIC) / cos(CONE ANGLE)). The chord is the
  projected chord AERO CHORD cos(CONE ANGLE) and t/c = TM / AERO CHORD / cos(CONE ANGLE),
  so that Aungier (9-2, 9-3) recovers the printed values. Rotor angles change
  sign: the reports give relative angles positive against rotation.
- Profile. The contract's multiple circular arc (Crouse, NASA TN D-7345):
  TURN RATE is its turning-rate ratio C1/C2; the transition point and the
  maximum-thickness point, printed as axial positions ZTC and ZMC, become
  chordwise fractions of the constructed meanline (the meanline turned by
  its stagger and scaled to the axial extent ZI-ZO). The meanline then
  reproduces the printed KTC within 0.14 deg and SETTING ANGLE within
  0.18 deg on all eight rows of stages 35-38. Edge radius TI / 2, the row
  mean (one value per row in the contract).
- Edge planes. The contract has one axial plane per edge; the mid-span (50
  percent) element's ZI and ZO are used.
- Passage. Axial origin moved to the inlet station; flow-path points between
  the inlet and outlet stations are kept, with the walls interpolated at both.
"""
import csv
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from sm_throughflow.contracts import SPAN_FRACTIONS
from sm_throughflow.correlations.blade_geometry import mca_meanline

CASES = Path(__file__).resolve().parents[1] / "cases"

ASSUMPTIONS = (
    "MCA sections from the printed turn rate, ZTC and ZMC (multiple_circular_arc)",
    "angles, chord and t/c mapped from the element cones to the axial-tangential plane with the printed cone angles",
    "edge planes at the mid-span element's ZI and ZO",
    "uniform inlet total state; inlet end-wall blockage from the measured inlet profile (inlet_blockage)",
)


#: Group headings some reports print above the geometry columns (TM X-3083, TP-1299: "RADII RI",
#: "BLADE ANGLES KIC", ...); stripped so every report's geometry reads with Table III's names.
GROUP_PREFIXES = ("RADII ", "BLADE ANGLES ", "BLADE THICKNESSES ", "AXIAL DIMENSIONS ")


def _read(path):
    """Rows of a transcribed CSV (headings row, units row, data); '?' marks are dropped, the value kept."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    heads, data = rows[0], rows[2:]
    return [{h: v.rstrip("?") for h, v in zip(heads, r)} for r in data]


#: Edge columns named after the meanline intercepts in some reports (TP-2049: ZIC, ZOC).
COLUMN_ALIASES = {"ZIC": "ZI", "ZOC": "ZO"}


def read_geometry(path):
    """A blade-geometry table with the group headings stripped from its column names."""
    def name(h):
        h = next((h[len(p):] for p in GROUP_PREFIXES if h.startswith(p)), h)
        return COLUMN_ALIASES.get(h, h)
    return [{name(h): v for h, v in r.items()} for r in _read(path)]


def _num(value):
    return float(value)


def _chordwise(camber, transition, turning_ratio, kappa_in, axial_fraction):
    """Chordwise fraction of the point of the MCA meanline at ``axial_fraction`` of its axial extent."""
    x, y, _, chi1 = mca_meanline(camber, transition, turning_ratio, 2001)
    g = math.radians(kappa_in - chi1)  # stagger: the chord's angle to the axial direction
    a = x * math.cos(g) - y * math.sin(g)
    return float(np.interp(axial_fraction, a / a[-1], x))


def _turn_for_front_camber(camber, transition, front):
    """Turning-rate ratio C1/C2 whose meanline turns through ``front`` degrees ahead of the transition."""
    def excess(t):
        _, _, kappa_t, chi1 = mca_meanline(camber, transition, t, 401)
        return (chi1 - kappa_t) - front
    return brentq(excess, 1e-4, 100.0)


def mca_element(row):
    """Transition point, turning-rate ratio and maximum-thickness point (chordwise) of an MCA element.

    Where the table prints TURN RATE (C1/C2; TP-1338 and its family) the transition point follows from
    ZTC. Where it prints X FACTOR instead (TP-2049, TM X-2926), C1/C2 follows from the blade angle at
    the transition point: the front segment turns through KIC - KTC, and both conditions (that front
    camber and the axial position ZTC) fix the transition point and C1/C2 together.
    """
    kic, koc = _num(row["KIC"]), _num(row["KOC"])
    camber = abs(kic - koc)
    zi, zo = _num(row["ZI"]), _num(row["ZO"])
    zt = (_num(row["ZTC"]) - zi) / (zo - zi)
    if "TURN RATE" in row:
        turn = _num(row["TURN RATE"])
        transition = brentq(lambda c: _chordwise(camber, c, turn, abs(kic), zt) - c, 0.05, 0.95)
    else:
        front = abs(kic - _num(row["KTC"]))

        def residual(c):
            return _chordwise(camber, c, _turn_for_front_camber(camber, c, front), abs(kic), zt) - c
        transition = brentq(residual, 0.05, 0.95)
        turn = _turn_for_front_camber(camber, transition, front)
    thickest = _chordwise(camber, transition, turn, abs(kic), (_num(row["ZMC"]) - zi) / (zo - zi))
    return transition, turn, thickest


def blade_row(table, row_id, stage_id, row_type, blade_count, clearance_m, profile="mca", camberline=None, max_camber_location=None):
    """One contract row from a blade-geometry CSV (lengths in cm, angles in degrees).

    ``profile`` "mca", "dca" or "c4"; ``camberline`` defaults to the profile's own (multiple or single
    circular arc), and ``max_camber_location`` is for a parabolic-arc camberline.
    """
    rows = read_geometry(table) if isinstance(table, (str, Path)) else list(table)
    tip = next(r for r in rows if r["RP"] == "TIP")
    hub = next(r for r in rows if r["RP"] == "HUB")
    mid = next(r for r in rows if _num(r["PERCENT SPAN"]) == 50.0)
    sign = -1.0 if row_type == "rotor" else 1.0

    def frac(r, key):
        return (_num(r[key]) - _num(hub[key])) / (_num(tip[key]) - _num(hub[key]))

    rows = sorted(rows, key=lambda r: _num(r["RI"]))  # hub to tip
    s_in = np.array([frac(r, "RI") for r in rows])
    s_out = np.array([frac(r, "RO") for r in rows])
    s_mid = 0.5 * (s_in + s_out)
    cone = np.radians([_num(r["CONE ANGLE"]) for r in rows])
    kic = np.radians([_num(r["KIC"]) for r in rows])
    koc = np.radians([_num(r["KOC"]) for r in rows])
    chord = np.array([_num(r["AERO CHORD"]) for r in rows])
    tm = np.array([_num(r["TM"]) for r in rows])
    k_in = sign * np.degrees(np.arctan(np.tan(kic) / np.cos(cone)))
    k_out = sign * np.degrees(np.arctan(np.tan(koc) / np.cos(cone)))
    chord_axt = chord * np.cos(cone) / 100.0
    t_c = tm / chord / np.cos(cone)
    edge = np.mean([0.25 * (_num(r["TI"]) + _num(r["TO"])) / _num(r["AERO CHORD"]) for r in rows])
    span = np.asarray(SPAN_FRACTIONS)

    def on_grid(s, values):
        return [round(float(v), 6) for v in np.interp(span, s, values)]

    row = {
        "row_id": row_id, "stage_id": stage_id, "row_type": row_type,
        "leading_edge_axial_m": _num(mid["ZI"]) / 100.0, "trailing_edge_axial_m": _num(mid["ZO"]) / 100.0,
        "blade_count": int(blade_count), "profile": profile,
        "camberline": camberline or ("multiple_circular_arc" if profile == "mca" else "circular_arc"),
        "edge_radius_to_chord": round(float(edge), 6),
        "metal_angle_in_deg": on_grid(s_in, k_in), "metal_angle_out_deg": on_grid(s_out, k_out),
        "chord_m": on_grid(s_mid, chord_axt), "thickness_to_chord": on_grid(s_mid, t_c),
    }
    if profile not in ("dca", "mca"):
        del row["edge_radius_to_chord"]  # the contract's other profiles carry their own edge shape
    if max_camber_location is not None:
        row["max_camber_location"] = round(float(max_camber_location), 4)
    if profile == "mca":
        transition, turn, thickest = map(np.array, zip(*[mca_element(r) for r in rows]))
        row.update(transition_point=on_grid(s_mid, transition), turning_rate_ratio=on_grid(s_mid, turn),
                   max_thickness_location=on_grid(s_mid, thickest))
    if row_type == "rotor":
        row["tip_clearance_m"] = clearance_m
    else:
        row["hub_clearance_m"] = clearance_m
    return row


def passage(inner_csv, outer_csv, z_in_cm, z_out_cm):
    """Passage stations between two axial planes (cm in the reports' frame), origin at ``z_in_cm``."""
    inner = [(_num(r["Axial distance"]), _num(r["Radius"])) for r in _read(inner_csv)]
    outer = [(_num(r["Axial distance"]), _num(r["Radius"])) for r in _read(outer_csv)]
    zi, ri = map(np.array, zip(*inner))
    zo, ro = map(np.array, zip(*outer))
    z = np.unique(np.concatenate([zi, zo, [z_in_cm, z_out_cm]]))
    z = z[(z >= z_in_cm) & (z <= z_out_cm)]
    return [{"axial_m": round((float(x) - z_in_cm) / 100.0, 7), "hub_radius_m": round(float(np.interp(x, zi, ri)) / 100.0, 7),
             "shroud_radius_m": round(float(np.interp(x, zo, ro)) / 100.0, 7)} for x in z]


def passage_table(path, z_in_cm, z_out_cm):
    """Passage stations from a one-table flow path (axial position, inner radius, outer radius; cm).

    A blank radius cell is printed with an arrow to the next printed value (constant radius), so
    each wall is interpolated between its printed points and held beyond them.
    """
    with open(path, newline="") as f:
        rows = list(csv.reader(f))[2:]
    walls = []
    for col in (1, 2):
        pts = [(_num(r[0]), _num(r[col])) for r in rows if r[col].strip()]
        walls.append(tuple(map(np.array, zip(*pts))))
    (zi, ri), (zo, ro) = walls
    z = np.unique(np.concatenate([zi, zo, [z_in_cm, z_out_cm]]))
    z = z[(z >= z_in_cm) & (z <= z_out_cm)]
    return [{"axial_m": round((float(x) - z_in_cm) / 100.0, 7), "hub_radius_m": round(float(np.interp(x, zi, ri)) / 100.0, 7),
             "shroud_radius_m": round(float(np.interp(x, zo, ro)) / 100.0, 7)} for x in z]


def edge_points(table):
    """(z, r) of the hub and tip edges of a blade-geometry CSV (cm): [(ZI, RI), (ZO, RO)] for each wall."""
    rows = read_geometry(table)
    hub = next(r for r in rows if r["RP"] == "HUB")
    tip = next(r for r in rows if r["RP"] == "TIP")
    return ([(_num(hub["ZI"]), _num(hub["RI"])), (_num(hub["ZO"]), _num(hub["RO"]))],
            [(_num(tip["ZI"]), _num(tip["RI"])), (_num(tip["ZO"]), _num(tip["RO"]))])


#: Flow-path points this close to a blade edge (cm) give way to the table's edge radius.
EDGE_MARGIN_CM = 0.1


def passage_with_edges(path, tables, z_in_cm, z_out_cm):
    """Passage stations from a one-table flow path, with the blade tables' edge radii over the blade rows.

    Within a blade row (between its edge planes on that wall, widened by EDGE_MARGIN_CM) the printed flow-path points are replaced
    by the row table's hub and tip edge radii, which are printed to three decimals; elsewhere the flow
    path is used as in ``passage_table``.
    """
    with open(path, newline="") as f:
        rows = list(csv.reader(f))[2:]
    edges = [edge_points(t) for t in tables]
    walls = []
    for col, wall in ((1, 0), (2, 1)):
        spans = [(e[wall][0][0], e[wall][1][0]) for e in edges]
        pts = [(_num(r[0]), _num(r[col])) for r in rows if r[col].strip()]
        pts = [p for p in pts if not any(a - EDGE_MARGIN_CM <= p[0] <= b + EDGE_MARGIN_CM for a, b in spans)]
        pts += [p for e in edges for p in e[wall]]
        pts.sort()
        walls.append(tuple(map(np.array, zip(*pts))))
    (zi, ri), (zo, ro) = walls
    z = np.unique(np.concatenate([zi, zo, [z_in_cm, z_out_cm]]))
    z = z[(z >= z_in_cm) & (z <= z_out_cm)]
    return [{"axial_m": round((float(x) - z_in_cm) / 100.0, 7), "hub_radius_m": round(float(np.interp(x, zi, ri)) / 100.0, 7),
             "shroud_radius_m": round(float(np.interp(x, zo, ro)) / 100.0, 7)} for x in z]


def stage_design(case, rotor_table, stator_table, flowpath, rotor_blades, stator_blades, tip_clearance_m, stator_hub_clearance_m,
                 z_in_cm, z_out_cm):
    folder = CASES / case
    rotor = blade_row(folder / rotor_table, "R1", "1", "rotor", rotor_blades, tip_clearance_m)
    stator = blade_row(folder / stator_table, "S1", "1", "stator", stator_blades, stator_hub_clearance_m)
    shift = z_in_cm / 100.0
    for row in (rotor, stator):
        row["leading_edge_axial_m"] = round(row["leading_edge_axial_m"] - shift, 7)
        row["trailing_edge_axial_m"] = round(row["trailing_edge_axial_m"] - shift, 7)
    stations = passage(folder / flowpath[0], folder / flowpath[1], z_in_cm, z_out_cm)
    return {"schema_version": "throughflow_design_v2", "machine_type": "compressor", "flow_path": "axial",
            "passage": {"stations": stations}, "rows": [rotor, stator]}


def read_overall(path):
    """Table IV of a Lewis report: {reading: {printed label: value}}, labels as printed."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    readings = rows[0][1:]
    out = {r: {} for r in readings}
    for row in rows[2:]:
        for reading, value in zip(readings, row[1:]):
            if value.strip():
                out[reading][row[0]] = _num(value.rstrip("?"))
    return out


def read_elements(path):
    """Blade-element data of a Lewis report: the printed rows, numbers as floats (hub last, as printed).
    "D-FACT" (TM X-3083, TP-1299, TM X-3101) is read as "D FACT" (TP-1338)."""
    return [{k.replace("D-FACT", "D FACT"): _num(v) for k, v in r.items() if v.strip()} for r in _read(path)]


#: Shape factor of the end-wall model's inlet layers (solver.endwall, section 8.8).
INLET_H1 = 1.4


def inlet_blockage(elements, hub_radius_cm, tip_radius_cm, resolution=0.005):
    """End-wall blockage at the rotor inlet from a measured inlet profile (one rule for every case).

    The end-wall model starts each wall's layer with H1 = 1.4, a power-law
    profile u/U = (y/delta)^n with n = (H1 - 1)/2 and delta* = delta n/(n + 1).
    The layer is fitted through the probe nearest each wall: its velocity
    ratio comes from its total-pressure deficit, u/U = sqrt((P0 - p)/(P0core - p)),
    with p from the core Mach number (the static pressure is taken uniform
    across the thin layer). When the deficit is below ``resolution`` (as a
    fraction of the core P0) the layer is taken to end at that probe, its
    largest thickness the data allow. The blockage is the sum of the two
    displacement thicknesses over the span.
    """
    n = 0.5 * (INLET_H1 - 1.0)
    span = tip_radius_cm - hub_radius_cm
    rows = sorted(elements, key=lambda r: r["RADII IN"])
    core = [r for r in rows if 15.0 <= r["PERCENT SPAN"] <= 85.0]
    p0_core = float(np.mean([r["TOTAL PRESS IN"] for r in core]))
    mach = float(np.mean([r["ABS MACH NO IN"] for r in core]))
    p_static = p0_core * (1.0 + 0.2 * mach ** 2) ** -3.5
    total = 0.0
    for probe, y in ((rows[0], rows[0]["RADII IN"] - hub_radius_cm), (rows[-1], tip_radius_cm - rows[-1]["RADII IN"])):
        deficit = (p0_core - probe["TOTAL PRESS IN"]) / p0_core
        if deficit < resolution:
            delta = y
        else:
            ratio = math.sqrt(max(probe["TOTAL PRESS IN"] - p_static, 0.0) / (p0_core - p_static))
            delta = y / ratio ** (1.0 / n)
        total += delta * n / (n + 1.0)
    return total / span


def task(points, total_pressure_pa=101325.0, total_temperature_k=288.15, inlet_blockage=0.02):
    """``points``: (name, mass flow kg/s, rpm) tuples."""
    return {
        "inlet": {"total_pressure_pa": total_pressure_pa, "total_temperature_k": total_temperature_k, "flow_angle_deg": 0.0},
        "operating_points": [{"name": n, "mass_flow_kg_s": float(m), "shaft_speed_rpm": float(rpm)} for n, m, rpm in points],
        "physics": {"physics_profile": "axial_compressor_aungier_v1", "inlet_blockage": inlet_blockage},
    }


#: The NASA Lewis single stages 35 to 38 (one rig and flow path, TP-1337). Inputs a report does not
#: give follow one rule for every case: tip clearance 0.4 mm, the running clearance measured on
#: Rotor 37 in this rig (TM-107310); stator hub gap 0 (no stator configuration is stated).
LEWIS_STAGES = {
    "nasa_stage35": dict(report="TP1338", rotor="rotor35", stator="stator35", blades=(36, 46), tip_clearance_m=4.0e-4,
                         clearance_source="not stated; rule value (Rotor 37, TM-107310)",
                         z_out_cm=10.640, z_out_source="not marked in TP-1338; the TP-1659 survey plane of the same rig"),
    "nasa_stage36": dict(report="TP1974", rotor="rotor36", stator="stator36", blades=(48, 62), tip_clearance_m=1.8e-4,
                         clearance_source="TP-1974 estimated running clearance 0.018 cm",
                         z_out_cm=8.890, z_out_source="TP-1974 survey plane"),
    "nasa_stage37": dict(report="TP1659", rotor="rotor37", stator="stator37", blades=(36, 46), tip_clearance_m=4.0e-4,
                         clearance_source="not stated; rule value (Rotor 37 alone in the same rig, TM-107310)",
                         z_out_cm=10.640, z_out_source="TP-1659 survey plane"),
    "nasa_stage38": dict(report="TP2001", rotor="rotor38", stator="stator38", blades=(48, 62), tip_clearance_m=4.0e-4,
                         clearance_source="not stated; rule value (Rotor 37, TM-107310)",
                         z_out_cm=8.890, z_out_source="TP-2001 survey plane"),
}
#: Station 1, the same survey plane in every report of the rig (cm from the rotor hub leading edge).
LEWIS_Z_IN_CM = -2.568


def lewis_stage_design(case_id, tip_clearance_m=None, stator_hub_clearance_m=0.0):
    c = LEWIS_STAGES[case_id]
    prefix = c["report"]
    return stage_design(
        case_id, "{}_tableIII_{}.csv".format(prefix, c["rotor"]), "{}_tableIII_{}.csv".format(prefix, c["stator"]),
        ("{}_fig1_flowpath_inner.csv".format(prefix), "{}_fig1_flowpath_outer.csv".format(prefix)), *c["blades"],
        c["tip_clearance_m"] if tip_clearance_m is None else tip_clearance_m, stator_hub_clearance_m, LEWIS_Z_IN_CM, c["z_out_cm"])


#: The NASA Lewis 50.8-cm fan stages (double-circular-arc rotor and stator). Rules where a report is
#: silent: tip clearance is the stated nominal cold clearance (no running value is given); stator hub
#: gap 0 (the stators are mounted in the casing with a hub retaining ring); station 3 is 2.011 cm
#: behind the stator mid-span trailing edge and station 1 at -2.408 cm, the survey planes TP-1299
#: gives for stage 53 in the same rig.
FAN_STAGES = {
    "nasa_stage52": dict(report="TMX3083", rotor="rotor52", stator="stator52", geometry=("tableIV", "tableV"), flowpath="fig1_flowpath",
                         blades=(30, 34), tip_clearance_m=5.0e-4, clearance_source="TM X-3083 nominal cold clearance 0.05 cm",
                         design_rpm=9741.3, stator_gap_scale=0.5,
                         stations_source="not given; the stage 53 survey planes (TP-1299) relative to the stator",
                         spacing_source="data at the 2-chord stator position: the printed 4-chord stator moved upstream by half its "
                                        "mid-span gap to the rotor (the 2-chord position is not tabulated)"),
    "nasa_stage53": dict(report="TP1299", rotor="rotor53", stator="stator53", geometry=("tableIV", "tableV"), flowpath="fig1_flowpath",
                         blades=(30, 38), tip_clearance_m=5.0e-4, clearance_source="TP-1299 nominal cold clearance 0.050 cm",
                         design_rpm=11459.2, stator_gap_scale=1.0, stations_source="TP-1299 Fig. 1 survey planes"),
    "nasa_stage55": dict(report="TMX3101", rotor="rotor55", stator="stator55", geometry=("tableIV", "tableV"), flowpath="fig1_flowpath",
                         blades=(15, 11), tip_clearance_m=6.0e-4, clearance_source="TM X-3101 nominal clearance 0.06 cm at the blade "
                                                                                 "centerline (about 0.08 cm at the edges)",
                         design_rpm=8019.3, stator_gap_scale=1.0, edge_radii=True,
                         stator_section=dict(profile="c4", camberline="parabolic_arc", max_camber_location=0.37),
                         section_source="stator 'NACA 400 Series airfoils' (not defined further): C.4 thickness on a parabolic arc "
                                        "with maximum camber at 0.37 chord, the Table V (ZMC - ZI)/(ZO - ZI); max. t/c 0.09",
                         stations_source="drawn only in Fig. 1; the stage 53 survey planes (TP-1299) relative to the rotor and stator"),
}
FAN_Z_IN_CM = -2.408
FAN_EXIT_GAP_CM = 32.492 - 30.481  # TP-1299: station 3 behind the stator 50-percent-span ZO


def fan_stage_design(case_id, tip_clearance_m=None, stator_hub_clearance_m=0.0):
    c = FAN_STAGES[case_id]
    folder = CASES / case_id
    p = c["report"]
    rotor = blade_row(folder / "{}_{}_{}.csv".format(p, c["geometry"][0], c["rotor"]), "R1", "1", "rotor", c["blades"][0],
                      c["tip_clearance_m"] if tip_clearance_m is None else tip_clearance_m, profile="dca")
    section = c.get("stator_section", dict(profile="dca"))
    stator = blade_row(folder / "{}_{}_{}.csv".format(p, c["geometry"][1], c["stator"]), "S1", "1", "stator", c["blades"][1],
                       stator_hub_clearance_m, **section)
    gap = stator["leading_edge_axial_m"] - rotor["trailing_edge_axial_m"]
    move = (c["stator_gap_scale"] - 1.0) * gap
    stator["leading_edge_axial_m"] += move
    stator["trailing_edge_axial_m"] += move
    z_out_cm = 100.0 * stator["trailing_edge_axial_m"] + FAN_EXIT_GAP_CM
    shift = FAN_Z_IN_CM / 100.0
    for row in (rotor, stator):
        row["leading_edge_axial_m"] = round(row["leading_edge_axial_m"] - shift, 7)
        row["trailing_edge_axial_m"] = round(row["trailing_edge_axial_m"] - shift, 7)
    flowpath = folder / "{}_{}.csv".format(p, c["flowpath"])
    if c.get("edge_radii"):
        tables = [folder / "{}_{}_{}.csv".format(p, c["geometry"][k], c[name]) for k, name in ((0, "rotor"), (1, "stator"))]
        stations = passage_with_edges(flowpath, tables, FAN_Z_IN_CM, z_out_cm)
    else:
        stations = passage_table(flowpath, FAN_Z_IN_CM, z_out_cm)
    return {"schema_version": "throughflow_design_v2", "machine_type": "compressor", "flow_path": "axial",
            "passage": {"stations": stations}, "rows": [rotor, stator]}, z_out_cm


#: Stage 8E-8 (TP-2049): one stage at four tip clearances. The report gives nominal nonrotating
#: clearances and a calculated wheel and blade growth plus eccentricity of about 0.040 cm at design
#: speed (pdf p5), so the running clearance is taken as nominal minus 0.040 cm; the larger clearances
#: were cut into the casing over the rotor (Fig. 5), a recess of at most 0.12 cm that is not modelled.
STAGE_8E = dict(folder="nasa_stage8e_tipclearance", report="TP2049", rotor="tableIV_rotor8E", stator="tableV_stator8",
                flowpath="fig2_flowpath", blades=(49, 54), design_rpm=16100.0, z_in_cm=-2.540, z_out_cm=13.462, growth_cm=0.040)
TIP_CLEARANCE_CASES = {"nasa_stage8e_c{:03d}".format(int(round(1000 * c))): c for c in (0.061, 0.102, 0.140, 0.178)}
#: Stage 8-8 (TM X-2926) is the same blading and rig (TP-2049 compares every cell of the tables), with a
#: nominal cold tip clearance of 0.05 cm; the TP-2049 growth estimate gives its running clearance.
STAGE_8_8_CLEARANCE_CM = 0.05


def stage8e_design(case_id, stator_hub_clearance_m=0.0):
    """Stage 8E-8 at one of its four clearances (TIP_CLEARANCE_CASES), or stage 8-8; multiple-circular-arc rows."""
    c = STAGE_8E
    folder = CASES / c["folder"]
    nominal_cm = STAGE_8_8_CLEARANCE_CM if case_id == "nasa_stage8_8" else TIP_CLEARANCE_CASES[case_id]
    running_cm = nominal_cm - c["growth_cm"]
    tables = [folder / "{}_{}.csv".format(c["report"], c[k]) for k in ("rotor", "stator")]
    rotor = blade_row(tables[0], "R1", "1", "rotor", c["blades"][0], running_cm / 100.0)
    stator = blade_row(tables[1], "S1", "1", "stator", c["blades"][1], stator_hub_clearance_m)
    shift = c["z_in_cm"] / 100.0
    for row in (rotor, stator):
        row["leading_edge_axial_m"] = round(row["leading_edge_axial_m"] - shift, 7)
        row["trailing_edge_axial_m"] = round(row["trailing_edge_axial_m"] - shift, 7)
    stations = passage_with_edges(folder / "{}_{}.csv".format(c["report"], c["flowpath"]), tables, c["z_in_cm"], c["z_out_cm"])
    return {"schema_version": "throughflow_design_v2", "machine_type": "compressor", "flow_path": "axial",
            "passage": {"stations": stations}, "rows": [rotor, stator]}


#: Earlier NASA Lewis transonic single stages on the 50.8-cm rig of stage 8E-8 (multiple circular arcs), whose
#: blade tables are printed in column parts (Table IV/V parts 1-3, joined on RP). Rules where a report is silent:
#: running clearance = nominal cold clearance less the 0.040-cm growth TP-2049 calculates for this rig; a
#: report without a stated clearance takes the family's 0.05 cm; design speed from the design tip speed and
#: the rotor's leading-edge tip radius.
LEWIS_MCA_STAGES = {
    "nasa_stage12_5": dict(report="TMX2658", rotor="rotor12", stator="stator5", blades=(56, 62), clearance_cm=None,
                           tip_speed=422.9, z_in_cm=-2.540, z_out_cm=13.462),
    "nasa_stage14_10": dict(report="TMX2645", rotor="rotor14", stator="stator10", blades=(43, 48), clearance_cm=0.05,
                            tip_speed=423.0, z_in_cm=-2.540, z_out_cm=13.462),
    "nasa_stage16_11": dict(report="TMX2904", rotor="rotor16", stator="stator11", blades=(44, 48), clearance_cm=0.05,
                            tip_speed=425.0, z_in_cm=-2.540, z_out_cm=12.700),
    "nasa_stage6_1": dict(report="TMX2731", rotor="rotor6", stator="stator1", blades=(47, 60), clearance_cm=0.05,
                          tip_speed=419.3, z_in_cm=-1.910, z_out_cm=12.950),
    "nasa_stage18_13": dict(report="TMX3100", rotor="rotor18", stator="stator13", blades=(56, 62), clearance_cm=0.05,
                            tip_speed=421.817, z_in_cm=-2.540, z_out_cm=13.462,
                            note="rotor part-span damper at about 52 percent span (TM X-3100), not modelled"),
}
FAMILY_CLEARANCE_CM = 0.05


def read_geometry_parts(folder, prefix):
    """A blade table printed in column parts (``<prefix>_part<N>.csv``), joined on RP."""
    rows = {}
    for path in sorted(folder.glob(prefix + "_part*.csv")):
        for r in read_geometry(path):
            rows.setdefault(r["RP"], {}).update(r)
    return list(rows.values())


def flowpath_points(path):
    """(z, r_inner, r_outer) points of a Fig. 1 flow-path table; '↓' (value continues) and blanks are skipped."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    units = rows[1]
    skip = 1 if units and not units[0].strip() and len(units) > 3 else 0
    walls = ([], [])
    for r in rows[2:]:
        r = r[skip:]
        if not r or not r[0].strip():
            continue
        for k in (0, 1):
            v = r[1 + k].strip() if len(r) > 1 + k else ""
            if v and v != "↓":
                walls[k].append((_num(r[0]), _num(v.rstrip("?"))))
    return walls


def mca_stage_design(case_id, stator_hub_clearance_m=0.0):
    """One of LEWIS_MCA_STAGES; returns (design, design_rpm, running clearance cm)."""
    c = LEWIS_MCA_STAGES[case_id]
    folder = CASES / case_id
    rotor_rows = read_geometry_parts(folder, "{}_tableIV_{}".format(c["report"], c["rotor"]))
    stator_rows = read_geometry_parts(folder, "{}_tableV_{}".format(c["report"], c["stator"]))
    running_cm = (c["clearance_cm"] or FAMILY_CLEARANCE_CM) - STAGE_8E["growth_cm"]
    rotor = blade_row(rotor_rows, "R1", "1", "rotor", c["blades"][0], running_cm / 100.0)
    stator = blade_row(stator_rows, "S1", "1", "stator", c["blades"][1], stator_hub_clearance_m)
    shift = c["z_in_cm"] / 100.0
    for row in (rotor, stator):
        row["leading_edge_axial_m"] = round(row["leading_edge_axial_m"] - shift, 7)
        row["trailing_edge_axial_m"] = round(row["trailing_edge_axial_m"] - shift, 7)
    (zi, ri), (zo, ro) = [tuple(map(np.array, zip(*sorted(w)))) for w in walls_with_edges(
        flowpath_points(next(folder.glob("{}_fig1_flowpath*.csv".format(c["report"])))), [rotor_rows, stator_rows])]
    z = np.unique(np.concatenate([zi, zo, [c["z_in_cm"], c["z_out_cm"]]]))
    z = z[(z >= c["z_in_cm"]) & (z <= c["z_out_cm"])]
    stations = [{"axial_m": round((float(x) - c["z_in_cm"]) / 100.0, 7), "hub_radius_m": round(float(np.interp(x, zi, ri)) / 100.0, 7),
                 "shroud_radius_m": round(float(np.interp(x, zo, ro)) / 100.0, 7)} for x in z]
    tip_in = float(next(r for r in rotor_rows if r["RP"] == "TIP")["RI"]) / 100.0
    rpm = c["tip_speed"] / tip_in * 60.0 / (2.0 * math.pi)
    design = {"schema_version": "throughflow_design_v2", "machine_type": "compressor", "flow_path": "axial",
              "passage": {"stations": stations}, "rows": [rotor, stator]}
    return design, rpm, running_cm


def walls_with_edges(walls, tables):
    """Flow-path wall points with the blade tables' edge radii over the blade rows (see passage_with_edges)."""
    out = []
    for wall, pts in enumerate(walls):
        edges = []
        for rows in tables:
            e = next(r for r in rows if r["RP"] == ("HUB" if wall == 0 else "TIP"))
            edges.append([(_num(e["ZI"]), _num(e["RI"])), (_num(e["ZO"]), _num(e["RO"]))])
        spans = [(a[0], b[0]) for a, b in edges]
        kept = [p for p in pts if not any(lo - EDGE_MARGIN_CM <= p[0] <= hi + EDGE_MARGIN_CM for lo, hi in spans)]
        out.append(kept + [p for e in edges for p in e])
    return out


#: Stage 66 (TM X-3345): the first stage of a five-stage core compressor, tested alone with its inlet
#: guide vanes set axial. Rotor 66 multiple circular arcs, stator 66 double circular arcs (pdf p5). The
#: Fig. 1 flow path has its own origin: its inner radius 12.700 at Z = 30.480 is the rotor hub RI, so
#: the rotor hub leading edge (the tables' origin) is taken at that Z (not stated). Station 1 lies
#: between the IGV trailing edge (2.50 cm ahead of the rotor hub leading edge) and the rotor; the IGV
#: is not modelled and the domain starts at its trailing-edge plane; station 3 follows the fan
#: stages' rule (FAN_EXIT_GAP_CM behind the stator mid-span ZO). Both are drawn only in Fig. 1.
#: Running tip clearance: the nominal cold 0.05 cm less the TP-2049 growth, as for the other stages
#: of this rig.
STAGE_66 = dict(folder="nasa_stage66_igv", report="TMX3345", rotor="tableIV_rotor66", stator="tableV_stator66",
                flowpath="fig1_flowpath", blades=(57, 64), clearance_cm=0.05, design_rpm=16042.3,
                flowpath_rotor_le_cm=30.480, z_in_cm=-2.50)


def stage66_design(stator_hub_clearance_m=0.0):
    """Stage 66 without its axial inlet guide vanes; returns (design, z_out_cm, running clearance cm)."""
    c = STAGE_66
    folder = CASES / c["folder"]
    running_cm = c["clearance_cm"] - STAGE_8E["growth_cm"]
    rotor_rows = read_geometry(folder / "{}_{}.csv".format(c["report"], c["rotor"]))
    stator_rows = read_geometry(folder / "{}_{}.csv".format(c["report"], c["stator"]))
    rotor = blade_row(rotor_rows, "R1", "1", "rotor", c["blades"][0], running_cm / 100.0)
    stator = blade_row(stator_rows, "S1", "1", "stator", c["blades"][1], stator_hub_clearance_m, profile="dca")
    mid = next(r for r in stator_rows if _num(r["PERCENT SPAN"]) == 50.0)
    z_in, z_out = c["z_in_cm"], _num(mid["ZO"]) + FAN_EXIT_GAP_CM
    for row in (rotor, stator):
        row["leading_edge_axial_m"] = round(row["leading_edge_axial_m"] - z_in / 100.0, 7)
        row["trailing_edge_axial_m"] = round(row["trailing_edge_axial_m"] - z_in / 100.0, 7)
    walls = [[(z - c["flowpath_rotor_le_cm"], r) for z, r in wall]
             for wall in flowpath_points(folder / "{}_{}.csv".format(c["report"], c["flowpath"]))]
    # Over the rotor the table edges lie on Fig. 1 within 0.02 cm; the stator TIP row (RO 25.121) lies
    # 0.3 cm outside the casing, so the stator keeps the Fig. 1 walls.
    (zi, ri), (zo, ro) = [tuple(map(np.array, zip(*sorted(w)))) for w in walls_with_edges(walls, [rotor_rows])]
    z = np.unique(np.concatenate([zi, zo, [z_in, z_out]]))
    z = z[(z >= z_in) & (z <= z_out)]
    stations = [{"axial_m": round((float(x) - z_in) / 100.0, 7), "hub_radius_m": round(float(np.interp(x, zi, ri)) / 100.0, 7),
                 "shroud_radius_m": round(float(np.interp(x, zo, ro)) / 100.0, 7)} for x in z]
    design = {"schema_version": "throughflow_design_v2", "machine_type": "compressor", "flow_path": "axial",
              "passage": {"stations": stations}, "rows": [rotor, stator]}
    return design, z_out, running_cm


def stage35(tip_clearance_m=4.0e-4, stator_hub_clearance_m=0.0):
    """NASA Stage 35 (TP-1338)."""
    return lewis_stage_design("nasa_stage35", tip_clearance_m, stator_hub_clearance_m)
