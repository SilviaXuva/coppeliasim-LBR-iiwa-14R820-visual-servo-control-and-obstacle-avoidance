from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import CameraFrame, JointCommand, RobotState


class ROS2BridgeInterface(ABC):
    """
    Boundary for ROS 2 integration.
    Internal types remain the canonical representation.
    """

    @abstractmethod
    def publish_robot_state(self, state: RobotState) -> None:
        raise NotImplementedError

    @abstractmethod
    def publish_joint_command(self, command: JointCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    def publish_camera_frame(self, frame: CameraFrame) -> None:
        raise NotImplementedError
