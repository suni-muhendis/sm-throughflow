"""Version 2 contracts: axial compressors on the streamline-curvature solver with Aungier's models.

The design owns the geometry: the passage and, for every blade row, its axial
extent, blade count, profile family and eleven span sections. The task owns
the operating points, the numerics, the gas and the physics profile, so a
design can never choose the referee that scores it. docs/throughflow_contract_v2.md
describes every field.
"""
import math
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import DESIGN_STREAMLINES, PassageGeometry

SIMULATOR_VERSION_V5 = "slc_aungier_experimental_v5"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


def _span_values(**kwargs):
    return Field(min_length=DESIGN_STREAMLINES, max_length=DESIGN_STREAMLINES, **kwargs)


class ShroudSealV2(StrictModel):
    """Labyrinth seal under a stator's inner shroud band (Aungier section 6.10)."""

    clearance_m: float = Field(gt=0)
    fin_count: int = Field(ge=1, le=12)
    fin_pitch_m: float = Field(gt=0)
    fin_thickness_m: float = Field(gt=0)


class BladeRowV2(StrictModel):
    """One blade row; angles in degrees from the axial direction, positive in the direction of rotation.

    The eleven section values run from hub (0) to shroud (1) at tenth-span
    intervals. ``metal_angle_in_deg`` applies at the leading-edge plane and
    ``metal_angle_out_deg`` at the trailing-edge plane; chord and thickness
    at the mid-chord plane. A rotor typically has negative angles (its
    relative flow approaches against the rotation), a stator positive inlet
    angles.
    """

    row_id: str = Field(min_length=1)
    stage_id: Optional[str] = None
    row_type: Literal["rotor", "stator"]
    leading_edge_axial_m: float = Field(ge=0)
    trailing_edge_axial_m: float = Field(gt=0)
    blade_count: int = Field(ge=2, le=400)
    profile: Literal["naca65", "c4", "dca"]
    camberline: Literal["naca65", "circular_arc", "parabolic_arc"]
    max_camber_location: float = Field(default=0.5, ge=0.3, le=0.7)
    edge_radius_to_chord: Optional[float] = Field(default=None, gt=0, le=0.05)
    metal_angle_in_deg: List[float] = _span_values()
    metal_angle_out_deg: List[float] = _span_values()
    chord_m: List[float] = _span_values()
    thickness_to_chord: List[float] = _span_values()
    tip_clearance_m: Optional[float] = Field(default=None, ge=0)
    hub_clearance_m: Optional[float] = Field(default=None, ge=0)
    shroud_seal: Optional[ShroudSealV2] = None

    @model_validator(mode="after")
    def valid(self):
        if self.trailing_edge_axial_m <= self.leading_edge_axial_m:
            raise ValueError("trailing_edge_axial_m must exceed leading_edge_axial_m")
        if any(c <= 0.0 for c in self.chord_m):
            raise ValueError("chord_m values must be positive")
        if any(not 0.0 < t < 1.0 for t in self.thickness_to_chord):
            raise ValueError("thickness_to_chord values must lie in (0, 1)")
        if self.camberline == "naca65" and self.max_camber_location != 0.5:
            raise ValueError("the naca65 camberline has its maximum camber at mid-chord")
        if self.camberline != "parabolic_arc" and self.max_camber_location != 0.5:
            raise ValueError("max_camber_location applies to the parabolic_arc camberline only")
        if (self.profile == "dca") != (self.edge_radius_to_chord is not None):
            raise ValueError("edge_radius_to_chord is required for, and only for, the dca profile")
        if self.row_type == "rotor":
            if self.tip_clearance_m is None:
                raise ValueError("a rotor requires tip_clearance_m")
            if self.hub_clearance_m is not None or self.shroud_seal is not None:
                raise ValueError("hub_clearance_m and shroud_seal are for stators")
        else:
            if self.tip_clearance_m is not None:
                raise ValueError("tip_clearance_m is for rotors; a stator has hub_clearance_m or a shroud_seal")
            if (self.hub_clearance_m is None) == (self.shroud_seal is None):
                raise ValueError("a stator has exactly one of hub_clearance_m (cantilevered) or shroud_seal (shrouded)")
        turning = [a - b for a, b in zip(self.metal_angle_in_deg, self.metal_angle_out_deg)]
        if not (all(t > 0.0 for t in turning) or all(t < 0.0 for t in turning)):
            raise ValueError("every section must turn the flow the same way (metal_angle_in - metal_angle_out of one sign)")
        return self


class ThroughflowDesignV2(StrictModel):
    schema_version: Literal["throughflow_design_v2"] = "throughflow_design_v2"
    machine_type: Literal["compressor"]
    flow_path: Literal["axial"]
    passage: PassageGeometry
    rows: List[BladeRowV2] = Field(min_length=1, max_length=80)

    @model_validator(mode="after")
    def topology(self):
        ids = [r.row_id for r in self.rows]
        if len(ids) != len(set(ids)):
            raise ValueError("row_id values must be unique")
        if not any(r.row_type == "rotor" for r in self.rows):
            raise ValueError("a compressor needs at least one rotor")
        for left, right in zip(self.rows, self.rows[1:]):
            if right.leading_edge_axial_m <= left.trailing_edge_axial_m:
                raise ValueError("rows must be axially ordered with a gap: {} starts before {} ends".format(right.row_id, left.row_id))
        first_rotor = next(i for i, r in enumerate(self.rows) if r.row_type == "rotor")
        for i, r in enumerate(self.rows):
            needs_stage = i > first_rotor or r.row_type == "rotor"
            if needs_stage and r.stage_id is None:
                raise ValueError("row {} needs a stage_id (only inlet guide vanes may omit it)".format(r.row_id))
        rotors = [r.stage_id for r in self.rows if r.row_type == "rotor"]
        if len(rotors) != len(set(rotors)):
            raise ValueError("each stage has exactly one rotor")
        return self

    @property
    def stage_count(self) -> int:
        return sum(r.row_type == "rotor" for r in self.rows)

    def inlet_guide_vanes(self) -> List[str]:
        """Stators ahead of the first rotor, which Aungier treats as inlet guide vanes."""
        first_rotor = next(i for i, r in enumerate(self.rows) if r.row_type == "rotor")
        return [r.row_id for r in self.rows[:first_rotor]]


class OperatingPointV2(StrictModel):
    name: str = Field(default="design", min_length=1)
    mass_flow_kg_s: float = Field(gt=0)
    shaft_speed_rpm: float = Field(gt=0)


class InletV2(StrictModel):
    total_pressure_pa: float = Field(gt=0)
    total_temperature_k: float = Field(gt=0)
    flow_angle_deg: float = Field(default=0.0, gt=-80.0, lt=80.0)


class GasV2(StrictModel):
    """A perfect gas; dry air by default."""

    cp_j_kg_k: float = Field(default=1004.5, gt=0)
    gas_constant_j_kg_k: float = Field(default=287.05, gt=0)

    @model_validator(mode="after")
    def physical(self):
        if self.cp_j_kg_k <= self.gas_constant_j_kg_k:
            raise ValueError("cp must exceed the gas constant")
        return self


class NumericsV2(StrictModel):
    stream_surfaces: int = Field(default=DESIGN_STREAMLINES, ge=5, le=41)
    curvature: Literal["full", "linear", "none"] = "full"
    tolerance: float = Field(default=1e-7, gt=0, le=1e-4)
    max_iterations: int = Field(default=400, ge=10, le=3000)


class PhysicsV2(StrictModel):
    physics_profile: Literal["axial_compressor_aungier_v1"] = "axial_compressor_aungier_v1"
    inlet_blockage: float = Field(default=0.02, ge=0.0, le=0.2)


class ThroughflowTaskV2(StrictModel):
    environment: Literal["turbomachinery_throughflow"] = "turbomachinery_throughflow"
    task_schema_version: Literal["throughflow_task_v2"] = "throughflow_task_v2"
    simulator_version: Literal["slc_aungier_experimental_v5"] = SIMULATOR_VERSION_V5
    inlet: InletV2
    operating_points: List[OperatingPointV2] = Field(min_length=1, max_length=12)
    gas: GasV2 = Field(default_factory=GasV2)
    physics: PhysicsV2 = Field(default_factory=PhysicsV2)
    numerics: NumericsV2 = Field(default_factory=NumericsV2)
    max_stages: int = Field(default=20, ge=1, le=40)

    @model_validator(mode="after")
    def unique_points(self):
        names = [p.name for p in self.operating_points]
        if len(names) != len(set(names)):
            raise ValueError("operating point names must be unique")
        return self

    def validate_design_ownership(self, design: ThroughflowDesignV2) -> None:
        if design.stage_count > self.max_stages:
            raise ValueError("design exceeds max_stages")


#: Frozen physics of each profile (docs/compressor_row_model.md); a task picks one by name.
AUNGIER_PROFILES: Dict[str, dict] = {
    "axial_compressor_aungier_v1": dict(
        K1=0.0073, max_loss=0.5, smoothing=True, shock_mean="arithmetic", endwall=True,
        maturity="candidate", reward_enabled=False,
        purpose="Aungier (2003) cascade, leakage and end-wall models on the SLC solver; pending validation.",
    ),
}
