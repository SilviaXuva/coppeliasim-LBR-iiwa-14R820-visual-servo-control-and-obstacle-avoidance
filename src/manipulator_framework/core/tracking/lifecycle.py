from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.tracking.track_state import TrackState
from manipulator_framework.core.types import TrackedTarget, TrackingStatus


@dataclass
class TrackLifecyclePolicy:
    """
    Minimal lifecycle policy for creating, aging and deleting tracks.
    """
    max_missed_steps: int = 3

    def create_track(self, track_id: str, target: TrackedTarget) -> TrackState:
        return TrackState(
            track_id=track_id,
            target_type=target.target_type,
            status=TrackingStatus.TENTATIVE,
            latest_detection=target.latest_detection,
            estimated_pose=target.estimated_pose,
            estimated_twist=target.estimated_twist,
            confidence=target.confidence,
            age_steps=1,
            missed_steps=0,
            timestamp=target.timestamp,
        )

    def mark_missed(self, track: TrackState, timestamp: float) -> TrackState:
        track.missed_steps += 1
        track.timestamp = timestamp

        if track.missed_steps > self.max_missed_steps:
            track.status = TrackingStatus.LOST
        return track

    def is_dead(self, track: TrackState) -> bool:
        return track.status is TrackingStatus.LOST
