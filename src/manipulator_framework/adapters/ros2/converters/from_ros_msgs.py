from __future__ import annotations

from typing import Any

import numpy as np

from manipulator_framework.core.types import CommandMode, JointCommand, TorqueCommand


def joint_command_from_ros_dict(data: dict[str, Any]) -> JointCommand:
    """
    Convert a ROS-facing command payload into an internal JointCommand.
    """
    raw_values = data.get("values", data.get("positions"))
    if raw_values is None:
        raise KeyError("ROS joint command payload must contain 'values' or 'positions'.")

    mode_raw = str(data.get("mode", "position")).lower()
    mode = CommandMode(mode_raw)

    joint_names = list(data.get("joint_names", ()))
    return JointCommand(
        values=np.asarray(raw_values, dtype=float),
        mode=mode,
        joint_names=joint_names,
        timestamp=float(data.get("timestamp", 0.0)),
    )


def torque_command_from_ros_dict(data: dict[str, Any]) -> TorqueCommand:
    """
    Convert a ROS-facing torque payload into an internal TorqueCommand.
    """
    raw_torques = data.get("torques")
    if raw_torques is None:
        raise KeyError("ROS torque command payload must contain 'torques'.")

    return TorqueCommand(
        torques=np.asarray(raw_torques, dtype=float),
        joint_names=tuple(data.get("joint_names", ())),
        timestamp=float(data.get("timestamp", 0.0)),
    )
