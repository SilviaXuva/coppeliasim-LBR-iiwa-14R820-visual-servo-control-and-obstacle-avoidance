from __future__ import annotations

from dataclasses import asdict
from typing import Any

from manipulator_framework.core.types import JointCommand, RobotState


def robot_state_to_ros_dict(state: RobotState) -> dict[str, Any]:
    """
    Convert an internal RobotState into a ROS-friendly dictionary placeholder.

    This module must be the only place that knows ROS DTO structure.
    """
    return asdict(state)


def joint_command_to_ros_dict(command: JointCommand) -> dict[str, Any]:
    """
    Convert an internal JointCommand into a ROS-friendly dictionary placeholder.

    Placeholder implementation until concrete ROS message classes are added.
    """
    return asdict(command)
