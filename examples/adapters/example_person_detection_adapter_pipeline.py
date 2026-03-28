from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.vision.yolo.yolo_ultralytics_adapter import YoloUltralyticsAdapter
from manipulator_framework.core.types import CameraFrame


class FakeYoloAdapter(YoloUltralyticsAdapter):
    def _infer(self, frame: CameraFrame):
        return [
            {"bbox": [20, 30, 80, 140], "confidence": 0.93, "class_name": "person"},
            {"bbox": [0, 0, 10, 10], "confidence": 0.10, "class_name": "person"},
        ]

    def _to_person_detection(self, raw_item, timestamp: float):
        if raw_item["class_name"] != "person":
            return None
        if raw_item["confidence"] < self.confidence_threshold:
            return None

        from manipulator_framework.core.types import PersonDetection

        x1, y1, x2, y2 = raw_item["bbox"]
        return PersonDetection(
            bbox_xyxy=(float(x1), float(y1), float(x2), float(y2)),
            confidence=float(raw_item["confidence"]),
            keypoints=None,
            frame_id="camera",
            timestamp=timestamp,
        )


def main() -> None:
    frame = CameraFrame(
        color=np.zeros((128, 128, 3), dtype=np.uint8),
        depth=None,
        intrinsics={},
        extrinsics=None,
        frame_id="camera",
        timestamp=0.1,
    )

    detector = FakeYoloAdapter(model=object(), confidence_threshold=0.25)
    detections = detector.detect(frame)

    print("Person detections:", detections)


if __name__ == "__main__":
    main()
