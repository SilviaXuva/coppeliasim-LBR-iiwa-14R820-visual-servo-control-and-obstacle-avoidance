from __future__ import annotations

from manipulator_framework.core.tracking import TrackLifecyclePolicy, TrackState
from manipulator_framework.core.types import TargetType, TrackingStatus


def test_track_is_marked_lost_after_too_many_misses() -> None:
    policy = TrackLifecyclePolicy(max_missed_steps=2)
    track = TrackState(
        track_id="track_0001",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        timestamp=0.0,
    )

    policy.mark_missed(track, 1.0)
    policy.mark_missed(track, 2.0)
    policy.mark_missed(track, 3.0)

    assert track.status is TrackingStatus.LOST
    assert policy.is_dead(track) is True
