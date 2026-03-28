from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.tracking.track_state import TrackState
from manipulator_framework.core.types import TrackedTarget, TrackingStatus


@dataclass
class TrackUpdater:
    """
    Update internal track state from a matched target observation/state estimate.
    """

    def update(self, track: TrackState, observation: TrackedTarget) -> TrackState:
        track.latest_detection = observation.latest_detection
        track.estimated_pose = observation.estimated_pose
        track.estimated_twist = observation.estimated_twist
        track.confidence = observation.confidence
        track.timestamp = observation.timestamp
        track.age_steps += 1
        track.missed_steps = 0

        if track.age_steps >= 2:
            track.status = TrackingStatus.TRACKED
        else:
            track.status = TrackingStatus.TENTATIVE

        return track
