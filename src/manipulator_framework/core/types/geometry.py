from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from .aliases import FrameName, Timestamp
from .mixins import SerializableMixin


def _as_vector(data: np.ndarray | list[float] | tuple[float, ...], expected_size: int, name: str) -> np.ndarray:
    arr = np.asarray(data, dtype=float).reshape(-1)
    if arr.size != expected_size:
        raise ValueError(f"{name} must have size {expected_size}, got {arr.size}.")
    return arr


@dataclass(frozen=True)
class Pose3D(SerializableMixin):
    """
    Internal rigid pose representation.

    position: [x, y, z]
    orientation_quat_xyzw: quaternion in XYZW convention
    """
    position: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    orientation_quat_xyzw: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0], dtype=float))
    frame_id: FrameName = "world"
    child_frame_id: FrameName = "object"
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "position", _as_vector(self.position, 3, "position"))
        object.__setattr__(
            self,
            "orientation_quat_xyzw",
            _as_vector(self.orientation_quat_xyzw, 4, "orientation_quat_xyzw"),
        )


@dataclass(frozen=True)
class Twist(SerializableMixin):
    """
    Internal spatial velocity representation.

    linear: [vx, vy, vz]
    angular: [wx, wy, wz]
    """
    linear: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    angular: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    frame_id: FrameName = "world"
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "linear", _as_vector(self.linear, 3, "linear"))
        object.__setattr__(self, "angular", _as_vector(self.angular, 3, "angular"))
