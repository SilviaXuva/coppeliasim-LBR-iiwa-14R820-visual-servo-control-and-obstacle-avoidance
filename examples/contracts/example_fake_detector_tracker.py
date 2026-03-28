from __future__ import annotations

import numpy as np

from manipulator_framework.core.contracts import (
    PersonDetectorInterface,
    TrackerInterface,
)
from manipulator_framework.core.types import (
    CameraFrame,
    Detection2D,
    PersonDetection,
    TargetType,
    TrackedTarget,
    TrackingStatus,
)


class FakePersonDetector(PersonDetectorInterface):
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        detection = Detection2D(
            bbox_xyxy=(100.0, 80.0, 220.0, 300.0),
            confidence=0.95,
            class_id=0,
            class_name="person",
            image_size_wh=(frame.image.shape[1], frame.image.shape[0]),
            timestamp=frame.timestamp,
        )
        return [
            PersonDetection(
                detection=detection,
                keypoints_uv=((140.0, 100.0), (150.0, 150.0)),
                person_id_hint="candidate_1",
                timestamp=frame.timestamp,
            )
        ]


class FakeTracker(TrackerInterface):
    def update(self, detections: list[Detection2D], timestamp: float) -> list[TrackedTarget]:
        tracks: list[TrackedTarget] = []
        for idx, detection in enumerate(detections):
            tracks.append(
                TrackedTarget(
                    target_id=f"track_{idx}",
                    target_type=TargetType.PERSON,
                    status=TrackingStatus.TRACKED,
                    latest_detection=detection,
                    confidence=detection.confidence,
                    age_steps=1,
                    missed_steps=0,
                    timestamp=timestamp,
                )
            )
        return tracks

    def reset(self) -> None:
        pass


def main() -> None:
    frame = CameraFrame(
        image=np.zeros((480, 640, 3), dtype=np.uint8),
        camera_id="fake_camera",
        frame_id="camera_frame",
        timestamp=1.5,
    )

    detector = FakePersonDetector()
    tracker = FakeTracker()

    people = detector.detect_people(frame)
    detections = [p.detection for p in people]
    tracks = tracker.update(detections, frame.timestamp)

    print("People detections:", [p.to_dict() for p in people])
    print("Tracks:", [t.to_dict() for t in tracks])


if __name__ == "__main__":
    main()
