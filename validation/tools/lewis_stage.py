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


def _read(path):
    """Rows of a transcribed CSV (headings row, units row, data); '?' marks are dropped, the value kept."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    heads, data = rows[0], rows[2:]
    return [{h: v.rstrip("?") for h, v in zip(heads, r)} for r in data]


def _num(value):
    return float(value)


def _chordwise(camber, transition, turning_ratio, kappa_in, axial_fraction):
    """Chordwise fraction of the point of the MCA meanline at ``axial_fraction`` of its axial extent."""
    x, y, _, chi1 = mca_meanline(camber, transition, turning_ratio, 2001)
    g = math.radians(kappa_in - chi1)  # stagger: the chord's angle to the axial direction
    a = x * math.cos(g) - y * math.sin(g)
    return float(np.interp(axial_fraction, a / a[-1], x))


def mca_element(row):
    """Transition point and maximum-thickness point (chordwise fractions) of a Table III element."""
    kic, koc = _num(row["KIC"]), _num(row["KOC"])
    camber, turn = abs(kic - koc), _num(row["TURN RATE"])
    zi, zo = _num(row["ZI"]), _num(row["ZO"])
    zt = (_num(row["ZTC"]) - zi) / (zo - zi)
    transition = brentq(lambda c: _chordwise(camber, c, turn, abs(kic), zt) - c, 0.05, 0.95)
    thickest = _chordwise(camber, transition, turn, abs(kic), (_num(row["ZMC"]) - zi) / (zo - zi))
    return transition, turn, thickest


def blade_row(table, row_id, stage_id, row_type, blade_count, clearance_m):
    """One contract row from a Table III CSV (lengths in cm, angles in degrees)."""
    rows = _read(table)
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
    transition, turn, thickest = map(np.array, zip(*[mca_element(r) for r in rows]))
    edge = np.mean([0.25 * (_num(r["TI"]) + _num(r["TO"])) / _num(r["AERO CHORD"]) for r in rows])
    span = np.asarray(SPAN_FRACTIONS)

    def on_grid(s, values):
        return [round(float(v), 6) for v in np.interp(span, s, values)]

    row = {
        "row_id": row_id, "stage_id": stage_id, "row_type": row_type,
        "leading_edge_axial_m": _num(mid["ZI"]) / 100.0, "trailing_edge_axial_m": _num(mid["ZO"]) / 100.0,
        "blade_count": int(blade_count), "profile": "mca", "camberline": "multiple_circular_arc", "edge_radius_to_chord": round(float(edge), 6),
        "metal_angle_in_deg": on_grid(s_in, k_in), "metal_angle_out_deg": on_grid(s_out, k_out),
        "chord_m": on_grid(s_mid, chord_axt), "thickness_to_chord": on_grid(s_mid, t_c),
    }
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
    """Table V or VI of a Lewis report: the printed rows, numbers as floats (hub last, as printed)."""
    return [{k: _num(v) for k, v in r.items() if v.strip()} for r in _read(path)]


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


def stage35(tip_clearance_m=4.0e-4, stator_hub_clearance_m=0.0):
    """NASA Stage 35 (TP-1338)."""
    return lewis_stage_design("nasa_stage35", tip_clearance_m, stator_hub_clearance_m)
