"""sm_throughflow — experimental turbomachinery throughflow environment on sm-core.

Registered as ``turbomachinery_throughflow`` in the ``sm_core.environments``
entry-point group, so once this package is installed:

    from sm_core import make_env

    env = make_env("turbomachinery_throughflow")
    result = env.evaluate(task_id, task_params, design_id, design)
"""
from .contracts import DESIGN_STREAMLINES, DESIGN_STREAMTUBES, SPAN_FRACTIONS, ThroughflowDesignV2, ThroughflowTaskV2

__version__ = "0.1.0"


def make_env(**kwargs):
    """Build the throughflow environment; registered as ``turbomachinery_throughflow``.

    The imports are lazy so that discovering the environment stays cheap.
    """
    from .env import TurbomachineryThroughflowEnv
    from .score import ExperimentalThroughflowScore
    from .simulator import SlcAungierSimulator

    return TurbomachineryThroughflowEnv(SlcAungierSimulator(), ExperimentalThroughflowScore())


__all__ = ["make_env", "ThroughflowDesignV2", "ThroughflowTaskV2", "SPAN_FRACTIONS", "DESIGN_STREAMLINES", "DESIGN_STREAMTUBES"]
