from __future__ import annotations

from dataclasses import dataclass


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


class FakeRobot:
    def read_state(self) -> FakeRobotState:
        return FakeRobotState(
            joint_names=["j1", "j2"],
            positions=[0.0, 0.1],
            velocities=[0.0, 0.0],
            timestamp=0.0,
        )

    def send_command(self, command: FakeJointCommand) -> None:
        print("[robot] command received:", command)


class FakeROS2RobotBridge:
    def __init__(self, robot: FakeRobot) -> None:
        self._robot = robot

    def read_robot_state_message(self) -> dict:
        state = self._robot.read_state()
        return {
            "joint_names": state.joint_names,
            "positions": state.positions,
            "velocities": state.velocities,
            "timestamp": state.timestamp,
        }


class FakeROS2CommandBridge:
    def __init__(self, robot: FakeRobot) -> None:
        self._robot = robot

    def handle_command_message(self, payload: dict) -> None:
        command = FakeJointCommand(
            joint_names=payload["joint_names"],
            positions=payload.get("positions"),
            velocities=payload.get("velocities"),
            accelerations=payload.get("accelerations"),
            timestamp=payload["timestamp"],
        )
        self._robot.send_command(command)


def main() -> int:
    robot = FakeRobot()
    state_bridge = FakeROS2RobotBridge(robot)
    command_bridge = FakeROS2CommandBridge(robot)

    outgoing = state_bridge.read_robot_state_message()
    print("[ros2] outgoing state:", outgoing)

    incoming = {
        "joint_names": ["j1", "j2"],
        "positions": [0.2, 0.3],
        "velocities": None,
        "accelerations": None,
        "timestamp": 0.1,
    }
    command_bridge.handle_command_message(incoming)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
