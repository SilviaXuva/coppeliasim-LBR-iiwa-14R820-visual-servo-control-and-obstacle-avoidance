from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import (
    Detection2D,
    Pose3D,
    TargetType,
    TrackedTarget,
    TrackingStatus,
    Twist,
)


@dataclass
class TrackState:
    """
    Internal mutable state for a tracked target.
    """
    track_id: str
    target_type: TargetType
    status: TrackingStatus
    latest_detection: Detection2D | None = None
    estimated_pose: Pose3D | None = None
    estimated_twist: Twist | None = None
    confidence: float = 0.0
    age_steps: int = 0
    missed_steps: int = 0
    timestamp: float = 0.0

    def to_tracked_target(self) -> TrackedTarget:
        return TrackedTarget(
            target_id=self.track_id,
            target_type=self.target_type,
            status=self.status,
            latest_detection=self.latest_detection,
            estimated_pose=self.estimated_pose,
            estimated_twist=self.estimated_twist,
            confidence=self.confidence,
            age_steps=self.age_steps,
            missed_steps=self.missed_steps,
            timestamp=self.timestamp,
        )
