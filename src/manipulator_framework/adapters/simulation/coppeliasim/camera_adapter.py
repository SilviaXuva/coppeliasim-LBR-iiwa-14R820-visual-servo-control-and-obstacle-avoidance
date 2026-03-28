from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import CameraInterface
from manipulator_framework.core.types import CameraFrame


@dataclass
class CoppeliaSimCameraAdapter(CameraInterface):
    sim_client: Any
    camera_handle: Any
    frame_id: str = "sim_camera"

    def get_frame(self) -> CameraFrame:
        color = np.asarray(self._read_rgb_frame(), dtype=np.uint8)
        depth = self._read_depth_frame()

        return CameraFrame(
            color=color,
            depth=None if depth is None else np.asarray(depth, dtype=float),
            intrinsics=self.get_intrinsics(),
            extrinsics=self.get_extrinsics(),
            frame_id=self.frame_id,
            timestamp=self._read_time(),
        )

    def get_intrinsics(self) -> dict[str, float]:
        return self._read_intrinsics()

    def get_extrinsics(self) -> dict[str, Any] | None:
        return self._read_extrinsics()

    def _read_rgb_frame(self) -> Any:
        raise NotImplementedError("Bind CoppeliaSim RGB image API here.")

    def _read_depth_frame(self) -> Any:
        return None

    def _read_intrinsics(self) -> dict[str, float]:
        return {}

    def _read_extrinsics(self) -> dict[str, Any] | None:
        return None

    def _read_time(self) -> float:
        raise NotImplementedError("Bind CoppeliaSim simulation clock API here.")
