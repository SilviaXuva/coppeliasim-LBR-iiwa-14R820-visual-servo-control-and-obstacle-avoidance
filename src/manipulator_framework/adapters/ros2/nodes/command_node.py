from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.command_bridge import ROS2CommandBridge


class CommandNode:
    """Thin ROS 2 command node placeholder."""

    def __init__(self, bridge: ROS2CommandBridge) -> None:
        self._bridge = bridge

    def receive_once(self, payload: dict) -> None:
        """Placeholder method for receiving one command payload."""
        self._bridge.handle_command_message(payload)
