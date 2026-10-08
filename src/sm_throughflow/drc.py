"""Design-rule check: geometry the solver and Aungier's correlations can stand behind.

Each rule names its reason; docs/throughflow_contract_v2.md lists them. The
limits keep a design inside the data the correlations were fitted to (NASA
SP-36 cascades, Aungier chapter 6) and inside what a throughflow analysis can
represent.
"""
import math
from typing import Optional, Tuple

import numpy as np

from .contracts import SPAN_FRACTIONS, ThroughflowDesignV2
from .correlations.aungier import camberline_angles

MAX_METAL_ANGLE_DEG = 80.0
THICKNESS_RANGE = (0.02, 0.12)  # t_b/c of the cascade data behind (6-10), (6-25)
MAX_CAMBER_DEG = 70.0
SOLIDITY_RANGE = (0.3, 3.0)
AXIAL_CHORD_RATIO = (0.5, 1.5)  # chord cos(stagger) over the row's axial width
MAX_CLEARANCE_TO_SPAN = 0.05


def _radius(stations, x, name):
    return float(np.interp(x, [s.axial_m for s in stations], [getattr(s, name) for s in stations]))


def run_drc(design: ThroughflowDesignV2) -> Tuple[bool, Optional[str]]:
    stations = design.passage.stations
    x_in, x_out = stations[0].axial_m, stations[-1].axial_m
    span = np.asarray(SPAN_FRACTIONS, dtype=float)
    for row in design.rows:
        rid = row.row_id
        if not (x_in < row.leading_edge_axial_m and row.trailing_edge_axial_m < x_out):
            return False, "DRC Error: row {} must lie strictly inside the passage".format(rid)
        k_in = np.asarray(row.metal_angle_in_deg, dtype=float)
        k_out = np.asarray(row.metal_angle_out_deg, dtype=float)
        if np.any(np.abs(np.concatenate([k_in, k_out])) >= MAX_METAL_ANGLE_DEG):
            return False, "DRC Error: row {} metal angles must stay below {:g} degrees".format(rid, MAX_METAL_ANGLE_DEG)
        camber = np.abs(k_in - k_out)
        if np.any(camber > MAX_CAMBER_DEG):
            return False, "DRC Error: row {} camber exceeds {:g} degrees, beyond the cascade correlations".format(rid, MAX_CAMBER_DEG)
        t_c = np.asarray(row.thickness_to_chord, dtype=float)
        if np.any(t_c < THICKNESS_RANGE[0]) or np.any(t_c > THICKNESS_RANGE[1]):
            return False, "DRC Error: row {} thickness_to_chord must lie in [{:g}, {:g}], the range of the cascade data".format(rid, *THICKNESS_RANGE)
        x_mid = 0.5 * (row.leading_edge_axial_m + row.trailing_edge_axial_m)
        hub, shroud = _radius(stations, x_mid, "hub_radius_m"), _radius(stations, x_mid, "shroud_radius_m")
        height = shroud - hub
        chord = np.asarray(row.chord_m, dtype=float)
        pitch = 2.0 * math.pi * (hub + span * height) / row.blade_count
        solidity = chord / pitch
        if np.any(solidity < SOLIDITY_RANGE[0]) or np.any(solidity > SOLIDITY_RANGE[1]):
            return False, "DRC Error: row {} solidity {:.3g} to {:.3g} leaves [{:g}, {:g}]".format(rid, solidity.min(), solidity.max(), *SOLIDITY_RANGE)
        sign = 1.0 if np.mean(k_in - k_out) > 0 else -1.0
        chi1, _ = camberline_angles(camber, row.max_camber_location)
        stagger = sign * k_in - chi1
        axial = chord * np.abs(np.cos(np.radians(stagger))) / (row.trailing_edge_axial_m - row.leading_edge_axial_m)
        if np.any(axial < AXIAL_CHORD_RATIO[0]) or np.any(axial > AXIAL_CHORD_RATIO[1]):
            return False, "DRC Error: row {} axial chord (chord x cos stagger) is {:.2f} to {:.2f} times the leading-to-trailing-edge distance; it must lie in [{:g}, {:g}]".format(rid, axial.min(), axial.max(), *AXIAL_CHORD_RATIO)
        gap = row.tip_clearance_m if row.tip_clearance_m is not None else row.hub_clearance_m
        if gap is not None and gap >= MAX_CLEARANCE_TO_SPAN * height:
            return False, "DRC Error: row {} clearance is at least {:g}% of the blade height".format(rid, 100 * MAX_CLEARANCE_TO_SPAN)
        if row.shroud_seal is not None:
            seal = row.shroud_seal
            x2 = 1.058 + 0.0218 * seal.fin_count  # (6-96)
            if seal.clearance_m / seal.fin_pitch_m > x2 - 1.0:
                return False, "DRC Error: row {} seal clearance-to-pitch exceeds the limit of Egli's model (6-94)".format(rid)
            if seal.fin_pitch_m * (seal.fin_count - 1) + seal.fin_thickness_m > row.trailing_edge_axial_m - row.leading_edge_axial_m:
                return False, "DRC Error: row {} seal fins do not fit under the row".format(rid)
    return True, None
