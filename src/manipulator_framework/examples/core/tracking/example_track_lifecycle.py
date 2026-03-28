from __future__ import annotations

from manipulator_framework.core.tracking import NearestNeighborTracker
from manipulator_framework.core.types import Detection2D, TargetType, TrackedTarget, TrackingStatus


def make_target(t: float) -> TrackedTarget:
    detection = Detection2D(
        bbox_xyxy=(100.0, 100.0, 180.0, 260.0),
        confidence=0.95,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=t,
    )
    return TrackedTarget(
        target_id="candidate_person",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TENTATIVE,
        latest_detection=detection,
        confidence=0.95,
        timestamp=t,
    )


def main() -> None:
    tracker = NearestNeighborTracker()

    print("Create track")
    print(tracker.update([make_target(0.0)], timestamp=0.0))

    print("Promote track")
    print(tracker.update([make_target(1.0)], timestamp=1.0))

    print("Miss 1")
    print(tracker.update([], timestamp=2.0))

    print("Miss 2")
    print(tracker.update([], timestamp=3.0))

    print("Miss 3")
    print(tracker.update([], timestamp=4.0))

    print("Miss 4 -> removed")
    print(tracker.update([], timestamp=5.0))


if __name__ == "__main__":
    main()
