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
        target_id="observation_only",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TENTATIVE,
        latest_detection=detection,
        confidence=0.9,
        timestamp=t,
    )


def main() -> None:
    tracker = NearestNeighborTracker()

    sequence = [
        [make_target(100, 100, 200, 300, 0.0)],
        [make_target(108, 102, 208, 302, 1.0)],
        [make_target(116, 104, 216, 304, 2.0)],
    ]

    for step, observations in enumerate(sequence):
        tracks = tracker.update(observations, timestamp=float(step))
        print(f"step={step}")
        for track in tracks:
            print(track.to_dict())


if __name__ == "__main__":
    main()
