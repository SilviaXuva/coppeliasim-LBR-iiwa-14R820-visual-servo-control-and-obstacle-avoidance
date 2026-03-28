from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import ControlOutput, Pose3D, RobotState


class VisualServoInterface(ABC):
    """Visual servoing contract, independent from camera backend."""

    @abstractmethod
    def compute_control(
        self,
        robot_state: RobotState,
        current_target_pose: Pose3D,
        desired_target_pose: Pose3D,
    ) -> ControlOutput:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
