"""Scene object adapters for CoppeliaSim simulation."""

from .coppelia_conveyor_adapter import CoppeliaConveyorAdapter
from .coppelia_gripper_adapter import CoppeliaGripperAdapter
from .coppelia_object_adapter import CoppeliaObjectAdapter

__all__ = [
    "CoppeliaConveyorAdapter",
    "CoppeliaGripperAdapter",
    "CoppeliaObjectAdapter",
]
