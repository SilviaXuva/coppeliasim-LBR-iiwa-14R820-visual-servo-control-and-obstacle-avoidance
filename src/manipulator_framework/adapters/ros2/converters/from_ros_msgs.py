from __future__ import annotations

from typing import Any

from manipulator_framework.core.types import CommandMode, JointCommand


def joint_command_from_ros_dict(data: dict[str, Any]) -> JointCommand:
    """
    Convert a ROS-friendly dictionary placeholder into an internal JointCommand.
    """
    return JointCommand(
        values=data.get("positions"),
        mode=CommandMode.POSITION,
        joint_names=data["joint_names"],
        timestamp=data.get("timestamp", 0.0),
    )
