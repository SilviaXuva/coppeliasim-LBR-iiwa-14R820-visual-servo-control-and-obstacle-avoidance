from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.adapters.ros2.converters.to_ros_msgs import (
    joint_command_to_ros_dict,
    robot_state_to_ros_dict,
)


@dataclass
class FakeRobotState:
    joint_names: list[str]
    positions: list[float]
    velocities: list[float]
    timestamp: float


@dataclass
class FakeJointCommand:
    joint_names: list[str]
    positions: list[float] | None
    velocities: list[float] | None
    accelerations: list[float] | None
    timestamp: float


def test_robot_state_to_ros_dict_returns_expected_keys() -> None:
    state = FakeRobotState(
        joint_names=["j1", "j2"],
        positions=[0.1, 0.2],
        velocities=[0.0, 0.0],
        timestamp=1.23,
    )

    result = robot_state_to_ros_dict(state)

    assert result["joint_names"] == ["j1", "j2"]
    assert result["positions"] == [0.1, 0.2]
    assert result["velocities"] == [0.0, 0.0]
    assert result["timestamp"] == 1.23


def test_joint_command_to_ros_dict_returns_expected_keys() -> None:
    command = FakeJointCommand(
        joint_names=["j1", "j2"],
        positions=[0.5, 0.6],
        velocities=None,
        accelerations=None,
        timestamp=2.0,
    )

    result = joint_command_to_ros_dict(command)

    assert result["joint_names"] == ["j1", "j2"]
    assert result["positions"] == [0.5, 0.6]
    assert result["timestamp"] == 2.0
