from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.camera_bridge import ROS2CameraBridge


class PerceptionNode:
    """Thin ROS 2 perception-facing node placeholder."""

    def __init__(self, bridge: ROS2CameraBridge) -> None:
        self._bridge = bridge

    def publish_once(self) -> dict:
        """Placeholder method for publishing one camera frame payload."""
        return self._bridge.read_camera_frame_message()
