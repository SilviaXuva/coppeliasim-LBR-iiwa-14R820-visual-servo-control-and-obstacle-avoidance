"""Simulation adapters for CoppeliaSim.

This package provides adapters for interacting with CoppeliaSim simulation.
"""

# Base adapter (remains in root)
from .coppelia_adapter import CoppeliaAdapter

# Scene object adapters (re-exported for backward compatibility)
from .scene_objects.coppelia_conveyor_adapter import CoppeliaConveyorAdapter
from .scene_objects.coppelia_gripper_adapter import CoppeliaGripperAdapter
from .scene_objects.coppelia_object_adapter import CoppeliaObjectAdapter

# Visualization adapters (re-exported for backward compatibility)
from .visualization.coppelia_drawing_adapter import CoppeliaDrawingAdapter

__all__ = [
    "CoppeliaAdapter",
    "CoppeliaConveyorAdapter",
    "CoppeliaDrawingAdapter",
    "CoppeliaGripperAdapter",
    "CoppeliaObjectAdapter",
]
