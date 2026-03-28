from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.command_bridge import ROS2CommandBridge


class FakeRobot:
    def __init__(self) -> None:
        self.last_command = None

    def send_command(self, command) -> None:
        self.last_command = command


def test_command_bridge_converts_and_forwards_command() -> None:
    robot = FakeRobot()
    bridge = ROS2CommandBridge(robot=robot)

    payload = {
        "joint_names": ["j1", "j2"],
        "positions": [0.3, 0.7],
        "velocities": None,
        "accelerations": None,
        "timestamp": 2.5,
    }

    bridge.handle_command_message(payload)

    assert robot.last_command is not None
    assert robot.last_command.joint_names == ["j1", "j2"]
    assert robot.last_command.positions == [0.3, 0.7]
    assert robot.last_command.timestamp == 2.5
