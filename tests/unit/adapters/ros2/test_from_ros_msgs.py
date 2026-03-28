from __future__ import annotations

from manipulator_framework.adapters.ros2.converters.from_ros_msgs import (
    joint_command_from_ros_dict,
)


def test_joint_command_from_ros_dict_builds_internal_command() -> None:
    payload = {
        "joint_names": ["j1", "j2"],
        "positions": [0.2, 0.4],
        "velocities": None,
        "accelerations": None,
        "timestamp": 0.5,
    }

    command = joint_command_from_ros_dict(payload)

    assert command.joint_names == ["j1", "j2"]
    assert command.positions == [0.2, 0.4]
    assert command.velocities is None
    assert command.accelerations is None
    assert command.timestamp == 0.5
