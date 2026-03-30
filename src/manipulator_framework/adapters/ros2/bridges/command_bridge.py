from __future__ import annotations

from manipulator_framework.adapters.ros2.converters.from_ros_msgs import (
    joint_command_from_ros_dict,
    torque_command_from_ros_dict,
)
from manipulator_framework.core.contracts.robot_interface import RobotInterface


class ROS2CommandBridge:
    """Bridge incoming ROS command payloads to the internal robot interface."""

    def __init__(self, robot: RobotInterface) -> None:
        self._robot = robot

    def handle_command_message(self, payload: dict) -> None:
        """
        Backwards-compatible entry point that mirrors the tests' expectation.
        For now, it simply delegates to the joint-command handler.
        """
        self.handle_joint_command_message(payload)

    def handle_joint_command_message(self, payload: dict) -> None:
        command = joint_command_from_ros_dict(payload)
        if hasattr(self._robot, "send_command"):
            self._robot.send_command(command)
        else:
            # Fall back to the formal interface if available
            self._robot.send_joint_command(command)

    def handle_torque_command_message(self, payload: dict) -> None:
        command = torque_command_from_ros_dict(payload)
        self._robot.send_torque_command(command)
