from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.command_bridge import ROS2CommandBridge


class SpyRobot:
    def __init__(self) -> None:
        self.last_command = None

    def send_command(self, command) -> None:
        self.last_command = command


def test_command_bridge_outputs_internal_joint_command_shape() -> None:
    robot = SpyRobot()
    bridge = ROS2CommandBridge(robot=robot)

    payload = {
        "joint_names": ["j1", "j2"],
        "positions": [0.1, 0.2],
        "velocities": None,
        "accelerations": None,
        "timestamp": 0.0,
    }

    bridge.handle_command_message(payload)

    command = robot.last_command
    assert hasattr(command, "joint_names")
    assert hasattr(command, "positions")
    assert hasattr(command, "timestamp")
