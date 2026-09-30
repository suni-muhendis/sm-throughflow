from typing import Any, Dict, Optional
from sm_core import BaseScoreFunction
from sm_core import ScoreResult

class ExperimentalThroughflowScore(BaseScoreFunction):
    """Scores every design zero until physical acceptance is implemented."""
    VERSION = "throughflow_score_disabled_v1"
    def calculate_score(self, task_params: Dict[str, Any], metrics: Dict[str, Any], is_valid: bool=True, error_message: Optional[str]=None) -> ScoreResult:
        return ScoreResult(normalized_total=0.0, components={"experimental_backend": 0.0}, is_valid=is_valid, error_message=error_message)
