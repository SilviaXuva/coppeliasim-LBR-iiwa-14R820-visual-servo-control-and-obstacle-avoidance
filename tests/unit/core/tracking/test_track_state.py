from __future__ import annotations

from manipulator_framework.core.tracking import TrackState
from manipulator_framework.core.types import TargetType, TrackingStatus


def test_track_state_can_be_converted_to_tracked_target() -> None:
    track = TrackState(
        track_id="track_0001",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TENTATIVE,
        confidence=0.9,
        age_steps=1,
        timestamp=0.0,
    )

    target = track.to_tracked_target()

    assert target.target_id == "track_0001"
    assert target.target_type is TargetType.PERSON
