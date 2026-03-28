from __future__ import annotations

from manipulator_framework.adapters.ros2.converters.from_ros_msgs import (
    joint_command_from_ros_dict,
)
from manipulator_framework.core.contracts.robot_interface import RobotInterface


class ROS2CommandBridge:
    """Bridge incoming ROS command payloads to the internal robot interface."""

    def __init__(self, robot: RobotInterface) -> None:
        self._robot = robot

    def handle_command_message(self, payload: dict) -> None:
        """Convert and forward command payload to the internal robot interface."""
        command = joint_command_from_ros_dict(payload)
        self._robot.send_command(command)
