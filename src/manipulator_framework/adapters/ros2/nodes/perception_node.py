from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.camera_bridge import ROS2CameraBridge
from manipulator_framework.adapters.ros2.bridges.detection_bridge import ROS2DetectionBridge


class PerceptionNode:
    """Thin ROS 2 perception-facing node."""

    def __init__(
        self,
        camera_bridge: ROS2CameraBridge | None = None,
        detection_bridge: ROS2DetectionBridge | None = None,
        bridge: ROS2CameraBridge | None = None,
    ) -> None:
        # `bridge` is kept for backwards compatibility with tests that expect a single argument
        self._camera_bridge = camera_bridge or bridge
        self._detection_bridge = detection_bridge

        if self._camera_bridge is None:
            raise ValueError("A camera bridge must be provided.")

    def publish_once(self) -> dict:
        """Compatibility shim used by unit tests."""
        return self.publish_camera_once()

    def publish_camera_once(self) -> dict:
        return self._camera_bridge.read_camera_frame_message()

    def publish_people_once(self) -> list[dict]:
        if self._detection_bridge is None:
            return []
        return self._detection_bridge.read_person_detection_messages()
