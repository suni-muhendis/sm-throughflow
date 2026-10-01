import math
from typing import Any, Dict, Optional
from pydantic import ValidationError
from sm_core import BaseEnvironment
from .contracts import ThroughflowDesignV1, ThroughflowTaskV1
from .contracts_v2 import ThroughflowDesignV2, ThroughflowTaskV2


def _is_v2_design(design_params) -> bool:
    return isinstance(design_params, dict) and design_params.get("schema_version") == "throughflow_design_v2"


def _is_v2_task(task_params) -> bool:
    return isinstance(task_params, dict) and task_params.get("task_schema_version") == "throughflow_task_v2"


class TurbomachineryThroughflowEnv(BaseEnvironment):
    """The throughflow environment.

    Version 2 designs and tasks (axial compressors, simulator
    ``slc_aungier_experimental_v5``) run on the package's own
    streamline-curvature solver; version 1 contracts keep running on NASA
    turbo-design (simulator ``nasa_turbo_design_experimental_v4``). Each task
    names its simulator version, and ``evaluate`` hands it to the environment
    holding that simulator, so every result is stamped with the simulator
    that produced it.
    """

    name = "turbomachinery_throughflow"

    def __init__(self, simulator, score_function, alternates: Optional[Dict[str, "TurbomachineryThroughflowEnv"]] = None):
        super().__init__(simulator, score_function)
        self._alternates = dict(alternates or {})

    def evaluate(self, task_id: str, task_params: Dict[str, Any], design_id: str, design_params: Dict[str, Any]):
        version = task_params.get("simulator_version") if isinstance(task_params, dict) else None
        if version is None and isinstance(task_params, dict) and not _is_v2_task(task_params):
            version = ThroughflowTaskV1.model_fields["simulator_version"].default
        if version is not None and version != self.simulator.VERSION and version in self._alternates:
            return self._alternates[version].evaluate(task_id, task_params, design_id, design_params)
        return super().evaluate(task_id, task_params, design_id, design_params)

    def validate_schema(self, design_params: Dict[str, Any]):
        model = ThroughflowDesignV2 if _is_v2_design(design_params) else ThroughflowDesignV1
        try: model.model_validate(design_params); return True,None
        except ValidationError as exc: return False,"Schema Error: {}".format(exc)
    def run_drc(self, design_params: Dict[str, Any]):
        if _is_v2_design(design_params):
            from .drc_v2 import run_drc_v2
            return run_drc_v2(ThroughflowDesignV2.model_validate(design_params))
        design=ThroughflowDesignV1.model_validate(design_params)
        stations=design.passage.stations
        x_min,x_max=stations[0].axial_m,stations[-1].axial_m
        previous_exit=x_min
        for row in design.rows:
            if not x_min<=row.axial_location_m<=x_max:
                return False,"DRC Error: row {} lies outside the passage".format(row.row_id)
            if row.row_type not in ("stator","rotor"):
                continue
            leading_edge=row.axial_location_m-row.axial_chord_m
            if leading_edge<previous_exit-1e-12:
                return False,"DRC Error: blade row {} overlaps the preceding row".format(row.row_id)
            previous_exit=row.axial_location_m
            if any(abs(angle)>=89.0 for angle in row.metal_angle_in_deg+row.metal_angle_out_deg):
                return False,"DRC Error: row {} metal angles must remain below 89 degrees".format(row.row_id)
            if row.stagger_angle_deg is not None and any(abs(angle)>=85.0 for angle in row.stagger_angle_deg):
                return False,"DRC Error: row {} stagger angles must remain below 85 degrees".format(row.row_id)
            if row.trailing_edge_thickness_m is not None and row.trailing_edge_thickness_m>=0.2*row.axial_chord_m:
                return False,"DRC Error: row {} trailing edge is at least 20% of axial chord".format(row.row_id)
            hub=self._interpolate_station(stations,row.axial_location_m,"hub_radius_m")
            shroud=self._interpolate_station(stations,row.axial_location_m,"shroud_radius_m")
            span=shroud-hub
            if row.tip_clearance_m is not None and row.tip_clearance_m>=0.1*span:
                return False,"DRC Error: row {} tip clearance is at least 10% of span".format(row.row_id)
            if row.stagger_angle_deg is not None:
                mean_radius=0.5*(hub+shroud); pitch=2*math.pi*mean_radius/row.blade_count
                chord=max(row.axial_chord_m/abs(math.cos(math.radians(angle))) for angle in row.stagger_angle_deg)
                solidity=chord/pitch
                if not 0.2<=solidity<=4.0:
                    return False,"DRC Error: row {} mean solidity {:.3f} is outside [0.2, 4.0]".format(row.row_id,solidity)
        return True,None

    @staticmethod
    def _interpolate_station(stations,x,name):
        for left,right in zip(stations,stations[1:]):
            if left.axial_m<=x<=right.axial_m:
                fraction=(x-left.axial_m)/(right.axial_m-left.axial_m)
                return getattr(left,name)+fraction*(getattr(right,name)-getattr(left,name))
        return getattr(stations[-1],name)
    def prepare_simulation_inputs(self, design_params: Dict[str, Any], task_params: Dict[str, Any]):
        if _is_v2_task(task_params) != _is_v2_design(design_params):
            raise ValueError("a throughflow_task_v2 needs a throughflow_design_v2 and a v1 task a v1 design")
        if _is_v2_task(task_params):
            task=ThroughflowTaskV2.model_validate(task_params); design=ThroughflowDesignV2.model_validate(design_params); task.validate_design_ownership(design)
            return {"design":design.model_dump(mode="json"),"task":task.model_dump(mode="json")}
        task=ThroughflowTaskV1.model_validate(task_params); design=ThroughflowDesignV1.model_validate(design_params); task.validate_design_ownership(design)
        return {"design":design.model_dump(mode="json"),"task":task.model_dump(mode="json")}
