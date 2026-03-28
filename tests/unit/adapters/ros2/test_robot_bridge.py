from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.adapters.ros2.bridges.robot_bridge import ROS2RobotBridge


@dataclass
class FakeRobotState:
    joint_names: list[str]
    positions: list[float]
    velocities: list[float]
    timestamp: float


class FakeRobot:
    def read_state(self) -> FakeRobotState:
        return FakeRobotState(
            joint_names=["j1", "j2"],
            positions=[0.0, 0.1],
            velocities=[0.0, 0.0],
            timestamp=10.0,
        )


def test_robot_bridge_reads_internal_state_and_converts() -> None:
    bridge = ROS2RobotBridge(robot=FakeRobot())

    payload = bridge.read_robot_state_message()

    assert payload["joint_names"] == ["j1", "j2"]
    assert payload["positions"] == [0.0, 0.1]
    assert payload["timestamp"] == 10.0
