"""The turbomachinery throughflow environment: schema, design rules and simulation inputs."""
from typing import Any, Dict

from pydantic import ValidationError
from sm_core import BaseEnvironment, EvaluationResult

from .contracts import ThroughflowDesignV2, ThroughflowTaskV2


class TurbomachineryThroughflowEnv(BaseEnvironment):
    """Axial compressors on the package's streamline-curvature solver with Aungier's models.

    The design owns the geometry, the task owns the operating points,
    numerics, gas and physics profile; see docs/throughflow_contract_v2.md.
    """

    name = "turbomachinery_throughflow"

    def _run_pipeline(self, score_fn, task_id, task_params, design_id, design_params):
        """Keep failure evidence which the current sm-core pipeline discards.

        All operating points live in this simulator's task. Malformed tasks
        still raise before simulation, as required by the base contract.
        This adapter does not change sm-core or its result/status schema.
        """
        for status, check in (("schema_error", self.validate_schema), ("drc_error", self.run_drc)):
            valid, error = check(design_params)
            if not valid:
                from .outcomes import failure_evidence, geometry_failure_kind
                from .solver.errors import SolverError
                kind = "invalid_input" if status == "schema_error" else geometry_failure_kind(error or "")
                return EvaluationResult(task_id=task_id, design_id=design_id, status=status,
                                        score=score_fn.calculate_score(task_params, {}, is_valid=False, error_message=error),
                                        raw_simulation_output={"failure": failure_evidence(SolverError(error, kind=kind, component="admission"))},
                                        error_message=error)
        inputs = self.prepare_simulation_inputs(design_params, task_params)
        try:
            success, metrics, raw, error = self.simulator.simulate(inputs)
        except Exception as exc:
            success, metrics, error = False, {}, "Unexpected simulation crash: {}".format(exc)
            raw = {"failure": {"kind": "unexpected_simulation_error", "message": str(exc)}}
        return EvaluationResult(task_id=task_id, design_id=design_id,
                                status="success" if success else "simulation_error",
                                score=score_fn.calculate_score(task_params, metrics if success else {},
                                                               is_valid=success, error_message=error or None),
                                metrics=metrics if success else {}, raw_simulation_output=raw,
                                error_message=error or None)

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
