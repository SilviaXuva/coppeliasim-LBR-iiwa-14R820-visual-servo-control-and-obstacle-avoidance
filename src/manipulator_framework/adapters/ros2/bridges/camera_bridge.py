from __future__ import annotations

from manipulator_framework.adapters.ros2.converters.to_ros_msgs import camera_frame_to_ros_dict
from manipulator_framework.core.contracts.camera_interface import CameraInterface


class ROS2CameraBridge:
    """Bridge between CameraInterface and ROS-facing transport payloads."""

    def __init__(self, camera: CameraInterface) -> None:
        self._camera = camera

    def read_camera_frame_message(self) -> dict:
        # Prefer the generic `capture` used in tests; fall back to interface method.
        if hasattr(self._camera, "capture"):
            frame = self._camera.capture()
        else:
            frame = self._camera.get_frame()
        return camera_frame_to_ros_dict(frame)
