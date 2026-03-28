from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.core.contracts import PersonDetectorInterface
from manipulator_framework.core.types import CameraFrame, PersonDetection


@dataclass
class YoloUltralyticsAdapter(PersonDetectorInterface):
    model: Any
    confidence_threshold: float = 0.25

    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        raw_results = self._infer(frame)
        detections: list[PersonDetection] = []

        for item in raw_results:
            person = self._to_person_detection(item, frame.timestamp)
            if person is not None:
                detections.append(person)

        return detections

    def _infer(self, frame: CameraFrame) -> list[Any]:
        raise NotImplementedError("Bind Ultralytics model inference here.")

    def _to_person_detection(self, raw_item: Any, timestamp: float) -> PersonDetection | None:
        raise NotImplementedError("Convert YOLO output into PersonDetection.")
