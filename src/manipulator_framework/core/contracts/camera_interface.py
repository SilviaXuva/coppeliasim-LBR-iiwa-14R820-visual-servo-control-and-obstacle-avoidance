from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np

from manipulator_framework.core.types import CameraFrame, Pose3D


class CameraInterface(ABC):
    """Abstract boundary for camera acquisition."""

    @abstractmethod
    def get_frame(self) -> CameraFrame:
        """Acquire one camera frame."""
        raise NotImplementedError

    @abstractmethod
    def get_intrinsics(self) -> np.ndarray:
        """Return camera intrinsics as a 3x3 matrix."""
        raise NotImplementedError

    @abstractmethod
    def get_extrinsics(self) -> Pose3D | None:
        """Return camera extrinsics if available."""
        raise NotImplementedError
