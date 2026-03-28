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
            joint_names=["j1"],
            positions=[0.0],
            velocities=[0.0],
            timestamp=0.0,
        )


def test_robot_bridge_contract_returns_serializable_payload() -> None:
    bridge = ROS2RobotBridge(robot=FakeRobot())

    payload = bridge.read_robot_state_message()

    assert isinstance(payload, dict)
    assert "joint_names" in payload
    assert "positions" in payload
    assert "timestamp" in payload
