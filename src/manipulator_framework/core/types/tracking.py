from __future__ import annotations

from dataclasses import dataclass, field

from .aliases import Timestamp
from .enums import TargetType, TrackingStatus
from .geometry import Pose3D, Twist
from .mixins import SerializableMixin
from .vision import Detection2D


@dataclass(frozen=True)
class TrackedTarget(SerializableMixin):
    target_id: str
    target_type: TargetType
    status: TrackingStatus
    latest_detection: Detection2D | None = None
    estimated_pose: Pose3D | None = None
    estimated_twist: Twist | None = None
    confidence: float = 0.0
    age_steps: int = 0
    missed_steps: int = 0
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be in [0, 1].")


@dataclass(frozen=True)
class ObstacleState(SerializableMixin):
    obstacle_id: str
    pose: Pose3D
    velocity: Twist | None = None
    radius: float | None = None
    source: str = "unknown"
    confidence: float = 1.0
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        if self.radius is not None and self.radius < 0.0:
            raise ValueError("radius must be non-negative.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be in [0, 1].")
