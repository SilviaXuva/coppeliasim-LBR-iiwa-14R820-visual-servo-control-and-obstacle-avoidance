from __future__ import annotations

from dataclasses import asdict

from manipulator_framework.core.contracts.camera_interface import CameraInterface


class ROS2CameraBridge:
    """Bridge between CameraInterface and ROS transport."""

    def __init__(self, camera: CameraInterface) -> None:
        self._camera = camera

    def read_camera_frame_message(self) -> dict:
        """Read internal camera frame and convert to ROS-facing DTO placeholder."""
        frame = self._camera.capture()
        return asdict(frame)
