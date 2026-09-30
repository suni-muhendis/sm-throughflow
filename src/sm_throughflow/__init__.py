"""sm_throughflow — experimental turbomachinery throughflow environment on sm-core.

Registered as ``turbomachinery_throughflow`` in the ``sm_core.environments``
entry-point group, so once this package is installed:

    from sm_core import make_env

    env = make_env("turbomachinery_throughflow")
    result = env.evaluate(task_id, task_params, design_id, design)
"""
from .contracts import DESIGN_STREAMLINES, DESIGN_STREAMTUBES, SPAN_FRACTIONS, ThroughflowDesignV1, ThroughflowTaskV1, ThroughflowSimulationResultV1
from .profiles import PHYSICS_PROFILES, ThroughflowPhysicsProfile, get_physics_profile

__version__ = "0.1.0"


def make_env(**kwargs):
    """Build the throughflow environment; registered as ``turbomachinery_throughflow``.

    The imports are lazy so that discovering the environment does not import
    NASA turbo-design or Cantera.
    """
    from .env import TurbomachineryThroughflowEnv
    from .score import ExperimentalThroughflowScore
    from .simulator import NasaTurboDesignSimulator

    return TurbomachineryThroughflowEnv(NasaTurboDesignSimulator(), ExperimentalThroughflowScore())


__all__ = ["make_env", "ThroughflowDesignV1", "ThroughflowTaskV1", "ThroughflowSimulationResultV1", "ThroughflowPhysicsProfile", "PHYSICS_PROFILES", "get_physics_profile", "SPAN_FRACTIONS", "DESIGN_STREAMLINES", "DESIGN_STREAMTUBES"]
