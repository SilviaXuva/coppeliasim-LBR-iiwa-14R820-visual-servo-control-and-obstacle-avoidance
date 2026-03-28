from __future__ import annotations

from manipulator_framework.core.tracking import NearestNeighborAssociation, TrackState
from manipulator_framework.core.types import Detection2D, TargetType, TrackedTarget, TrackingStatus


def test_nearest_neighbor_association_matches_close_detection() -> None:
    track_detection = Detection2D(
        bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
        confidence=0.9,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=0.0,
    )
    track = TrackState(
        track_id="track_0000",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        latest_detection=track_detection,
        confidence=0.9,
        timestamp=0.0,
    )

    obs_detection = Detection2D(
        bbox_xyxy=(108.0, 104.0, 208.0, 304.0),
        confidence=0.88,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=1.0,
    )
    observation = TrackedTarget(
        target_id="obs_1",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TENTATIVE,
        latest_detection=obs_detection,
        confidence=0.88,
        timestamp=1.0,
    )

    association = NearestNeighborAssociation(max_distance=50.0)
    matches, unmatched_tracks, unmatched_targets = association.match([track], [observation])

    assert len(matches) == 1
    assert unmatched_tracks == []
    assert unmatched_targets == []
