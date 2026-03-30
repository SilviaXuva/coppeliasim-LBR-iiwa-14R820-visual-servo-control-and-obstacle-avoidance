from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import CameraInterface
from manipulator_framework.core.types import CameraFrame, Pose3D


@dataclass
class PyPlotCameraAdapter(CameraInterface):
    """
    Minimal PyPlot backend camera adapter.

    Expected backend API by convention:
    - current_frame()
    - current_time()
    - current_camera_intrinsics() optional
    - current_camera_extrinsics() optional
    """

    backend: Any
    camera_id: str = "pyplot_camera"
    frame_id: str = "camera"

    def get_frame(self) -> CameraFrame:
        image = np.asarray(self.backend.current_frame(), dtype=np.uint8)
        return CameraFrame(
            image=image,
            camera_id=self.camera_id,
            frame_id=self.frame_id,
            timestamp=float(self.backend.current_time()),
            intrinsics=self.get_intrinsics(),
            extrinsics=self.get_extrinsics(),
        )

    def get_intrinsics(self) -> np.ndarray:
        reader = getattr(self.backend, "current_camera_intrinsics", None)
        if callable(reader):
            intrinsics = np.asarray(reader(), dtype=float)
            if intrinsics.shape == (3, 3):
                return intrinsics
        return np.eye(3, dtype=float)

    def get_extrinsics(self) -> Pose3D | None:
        reader = getattr(self.backend, "current_camera_extrinsics", None)
        if not callable(reader):
            return None
        payload = reader()
        if payload is None:
            return None
        if isinstance(payload, Pose3D):
            return payload
        if isinstance(payload, dict):
            return Pose3D(
                position=payload.get("position", [0.0, 0.0, 0.0]),
                orientation_quat_xyzw=payload.get("orientation_quat_xyzw", [0.0, 0.0, 0.0, 1.0]),
                frame_id=str(payload.get("frame_id", "world")),
                child_frame_id=str(payload.get("child_frame_id", self.frame_id)),
                timestamp=float(payload.get("timestamp", self.backend.current_time())),
            )
        raise TypeError("PyPlot camera extrinsics must be Pose3D, dict or None.")

