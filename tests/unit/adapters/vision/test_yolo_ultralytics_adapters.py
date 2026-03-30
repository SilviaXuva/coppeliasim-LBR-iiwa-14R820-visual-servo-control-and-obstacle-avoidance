from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.vision.yolo.yolo_object_adapter import YoloObjectAdapter
from manipulator_framework.adapters.vision.yolo.yolo_ultralytics_adapter import (
    YoloUltralyticsAdapter,
)
from manipulator_framework.core.types import CameraFrame


class FakeBoxes:
    def __init__(self) -> None:
        self.xyxy = np.array(
            [
                [10.0, 20.0, 50.0, 80.0],
                [15.0, 10.0, 35.0, 30.0],
            ],
            dtype=float,
        )
        self.conf = np.array([0.95, 0.70], dtype=float)
        self.cls = np.array([0, 2], dtype=float)


class FakeKeypoints:
    def __init__(self) -> None:
        self.xy = np.array(
            [
                [[11.0, 21.0], [12.0, 22.0]],
                [[16.0, 11.0], [17.0, 12.0]],
            ],
            dtype=float,
        )


class FakeResult:
    def __init__(self) -> None:
        self.boxes = FakeBoxes()
        self.keypoints = FakeKeypoints()
        self.names = {0: "person", 2: "cube"}


class FakeYoloModel:
    def predict(self, image, conf=0.25, verbose=False):
        return [FakeResult()]


def test_yolo_person_adapter_filters_person_and_converts_output() -> None:
    adapter = YoloUltralyticsAdapter(
        model=FakeYoloModel(),
        confidence_threshold=0.5,
    )

    frame = CameraFrame(
        image=np.zeros((100, 120, 3), dtype=np.uint8),
        camera_id="cam_01",
        timestamp=3.0,
    )

    detections = adapter.detect_people(frame)

    assert len(detections) == 1
    detection = detections[0]
    assert detection.timestamp == 3.0
    assert detection.detection.class_name == "person"
    assert detection.detection.class_id == 0
    assert detection.detection.bbox_xyxy == (10.0, 20.0, 50.0, 80.0)
    assert len(detection.keypoints_uv) == 2


def test_yolo_object_adapter_returns_generic_detection2d() -> None:
    adapter = YoloObjectAdapter(
        model=FakeYoloModel(),
        confidence_threshold=0.5,
        excluded_class_names=("person",),
    )

    frame = CameraFrame(
        image=np.zeros((100, 120, 3), dtype=np.uint8),
        camera_id="cam_01",
        timestamp=4.0,
    )

    detections = adapter.detect_objects(frame)

    assert len(detections) == 1
    detection = detections[0]
    assert detection.class_name == "cube"
    assert detection.class_id == 2
    assert detection.bbox_xyxy == (15.0, 10.0, 35.0, 30.0)
    assert detection.timestamp == 4.0
