from __future__ import annotations

from typing import Protocol


Matrix3x3 = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]
Matrix4x4 = tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]


class CameraPort(Protocol):
    """Camera boundary for frame acquisition and calibration data."""

    def capture_frame(self) -> object:
        """Capture and return the latest frame representation."""

    def get_intrinsic_matrix(self) -> Matrix3x3:
        """Return camera intrinsics."""

    def get_distortion_coefficients(self) -> tuple[float, ...]:
        """Return distortion parameters."""

    def get_extrinsic_matrix(self) -> Matrix4x4:
        """Return camera pose transform in world frame."""
