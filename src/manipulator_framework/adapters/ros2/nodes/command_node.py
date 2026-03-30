from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.command_bridge import ROS2CommandBridge


class CommandNode:
    """Thin ROS 2 command node."""

    def __init__(self, bridge: ROS2CommandBridge) -> None:
        self._bridge = bridge

    def receive_once(self, payload: dict) -> None:
        """Alias kept for test/backwards compatibility."""
        self._bridge.handle_command_message(payload)

    def receive_joint_command_once(self, payload: dict) -> None:
        self._bridge.handle_joint_command_message(payload)

    def receive_torque_command_once(self, payload: dict) -> None:
        self._bridge.handle_torque_command_message(payload)
