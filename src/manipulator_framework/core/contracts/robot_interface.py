from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import JointCommand, Pose3D, RobotState, TorqueCommand


class RobotInterface(ABC):
    """Abstract boundary for robot state access and command actuation."""

    @abstractmethod
    def get_robot_state(self) -> RobotState:
        """Return the current robot state."""
        raise NotImplementedError

    @abstractmethod
    def send_joint_command(self, command: JointCommand) -> None:
        """Send a joint-space command to the robot."""
        raise NotImplementedError

    @abstractmethod
    def send_torque_command(self, command: TorqueCommand) -> None:
        """Send a torque command to the robot."""
        raise NotImplementedError

    @abstractmethod
    def get_end_effector_pose(self) -> Pose3D:
        """Return the current end-effector pose."""
        raise NotImplementedError
