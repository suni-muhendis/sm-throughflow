"""The turbomachinery throughflow environment: schema, design rules and simulation inputs."""
from typing import Any, Dict

from pydantic import ValidationError
from sm_core import BaseEnvironment

from .contracts import ThroughflowDesignV2, ThroughflowTaskV2


class TurbomachineryThroughflowEnv(BaseEnvironment):
    """Axial compressors on the package's streamline-curvature solver with Aungier's models.

    The design owns the geometry, the task owns the operating points,
    numerics, gas and physics profile; see docs/throughflow_contract_v2.md.
    """

    name = "turbomachinery_throughflow"

    def validate_schema(self, design_params: Dict[str, Any]):
        try:
            ThroughflowDesignV2.model_validate(design_params)
            return True, None
        except ValidationError as exc:
            return False, "Schema Error: {}".format(exc)

    def run_drc(self, design_params: Dict[str, Any]):
        from .drc import run_drc

        return run_drc(ThroughflowDesignV2.model_validate(design_params))

    def prepare_simulation_inputs(self, design_params: Dict[str, Any], task_params: Dict[str, Any]):
        task = ThroughflowTaskV2.model_validate(task_params)
        design = ThroughflowDesignV2.model_validate(design_params)
        task.validate_design_ownership(design)
        return {"design": design.model_dump(mode="json"), "task": task.model_dump(mode="json")}
