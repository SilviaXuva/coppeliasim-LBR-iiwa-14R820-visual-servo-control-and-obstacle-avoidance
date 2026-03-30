from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import CameraInterface
from manipulator_framework.core.types import CameraFrame, Pose3D


@dataclass
class CoppeliaSimCameraAdapter(CameraInterface):
    """
    Minimal CoppeliaSim camera adapter.

    Expected sim_client API by convention:
    - get_camera_rgb(camera_handle)
    - get_camera_depth(camera_handle) optional
    - get_camera_intrinsics(camera_handle)
    - get_camera_extrinsics(camera_handle) optional
    - get_sim_time()
    """

    sim_client: Any
    camera_handle: Any
    camera_id: str = "sim_camera"
    frame_id: str = "camera"

    def get_frame(self) -> CameraFrame:
        image = np.asarray(self._read_rgb_frame(), dtype=np.uint8)

        return CameraFrame(
            image=image,
            camera_id=self.camera_id,
            frame_id=self.frame_id,
            timestamp=self._read_time(),
            intrinsics=self.get_intrinsics(),
            extrinsics=self.get_extrinsics(),
        )

    def get_intrinsics(self) -> np.ndarray:
        return self._read_intrinsics()

    def get_extrinsics(self) -> Pose3D | None:
        return self._read_extrinsics()

    def _read_rgb_frame(self) -> np.ndarray:
        image = self._call_required("get_camera_rgb", camera_handle=self.camera_handle)
        return np.asarray(image, dtype=np.uint8)

    def _read_depth_frame(self) -> np.ndarray | None:
        image = self._call_optional("get_camera_depth", camera_handle=self.camera_handle)
        if image is None:
            return None
        return np.asarray(image, dtype=float)

    def _read_intrinsics(self) -> np.ndarray:
        intrinsics = self._call_required("get_camera_intrinsics", camera_handle=self.camera_handle)
        intrinsics = np.asarray(intrinsics, dtype=float)
        if intrinsics.shape != (3, 3):
            raise ValueError("CoppeliaSim camera intrinsics must have shape (3, 3).")
        return intrinsics

    def _read_extrinsics(self) -> Pose3D | None:
        payload = self._call_optional("get_camera_extrinsics", camera_handle=self.camera_handle)
        if payload is None:
            return None

        if isinstance(payload, Pose3D):
            return payload

        if isinstance(payload, dict):
            return Pose3D(
                position=payload.get("position", [0.0, 0.0, 0.0]),
                orientation_quat_xyzw=payload.get(
                    "orientation_quat_xyzw",
                    [0.0, 0.0, 0.0, 1.0],
                ),
                frame_id=payload.get("frame_id", "world"),
                child_frame_id=payload.get("child_frame_id", self.frame_id),
                timestamp=float(payload.get("timestamp", self._read_time())),
            )

        raise TypeError("Camera extrinsics must be Pose3D, dict or None.")

    def _read_time(self) -> float:
        return float(self._call_required("get_sim_time"))

    def _call_required(self, method_name: str, **kwargs: Any) -> Any:
        candidate = getattr(self.sim_client, method_name, None)
        if not callable(candidate):
            raise NotImplementedError(
                f"CoppeliaSim client must implement '{method_name}' for CoppeliaSimCameraAdapter."
            )
        return candidate(**kwargs)

    def _call_optional(self, method_name: str, **kwargs: Any) -> Any | None:
        candidate = getattr(self.sim_client, method_name, None)
        if callable(candidate):
            return candidate(**kwargs)
        return None
