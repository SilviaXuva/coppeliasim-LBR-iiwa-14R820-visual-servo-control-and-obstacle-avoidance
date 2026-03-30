from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from manipulator_framework.core.types import Pose3D, RobotState, Trajectory


class VisualServoInterface(ABC):
    """Visual servoing contract for reference generation."""

    @abstractmethod
    def compute_reference(
        self,
        robot_state: RobotState,
        current_target_pose: Pose3D,
        desired_target_pose: Pose3D,
        dt: float,
    ) -> tuple[Any, Trajectory]:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
