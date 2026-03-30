from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import Pose3D


@dataclass(frozen=True)
class VisualError:
    """
    PBVS visual error in pose space.

    Placeholder:
        Orientation error is represented here by direct quaternion difference
        for architectural skeleton purposes. A more rigorous SE(3) error model
        can replace this later without changing the public flow.
    """
    position_error: np.ndarray
    orientation_error: np.ndarray

    @property
    def translation_error(self) -> float:
        return float(np.linalg.norm(self.position_error))

    @property
    def orientation_error_norm(self) -> float:
        return float(np.linalg.norm(self.orientation_error))

    @property
    def norm(self) -> float:
        return self.translation_error + self.orientation_error_norm


def compute_pose_error(current: Pose3D, desired: Pose3D) -> VisualError:
    position_error = np.asarray(desired.position, dtype=float) - np.asarray(current.position, dtype=float)
    orientation_error = (
        np.asarray(desired.orientation_quat_xyzw, dtype=float)
        - np.asarray(current.orientation_quat_xyzw, dtype=float)
    )

    return VisualError(
        position_error=position_error,
        orientation_error=orientation_error,
    )
