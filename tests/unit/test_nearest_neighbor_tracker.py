from __future__ import annotations

from manipulator_framework.core.tracking import NearestNeighborTracker
from manipulator_framework.core.types import Detection2D, TargetType, TrackedTarget, TrackingStatus


def make_target(x1: float, y1: float, x2: float, y2: float, t: float) -> TrackedTarget:
    detection = Detection2D(
        bbox_xyxy=(x1, y1, x2, y2),
        confidence=0.9,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=t,
    )
    return TrackedTarget(
        target_id="obs",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TENTATIVE,
        latest_detection=detection,
        confidence=0.9,
        timestamp=t,
    )


def test_tracker_keeps_same_track_for_close_observations() -> None:
    tracker = NearestNeighborTracker()

    tracks_1 = tracker.update([make_target(100, 100, 200, 300, 0.0)], timestamp=0.0)
    tracks_2 = tracker.update([make_target(108, 104, 208, 304, 1.0)], timestamp=1.0)

    assert len(tracks_1) == 1
    assert len(tracks_2) == 1
    assert tracks_1[0].target_id == tracks_2[0].target_id
