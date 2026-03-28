from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.core.contracts import MarkerDetectorInterface
from manipulator_framework.core.types import CameraFrame, MarkerDetection


@dataclass
class ArucoOpenCVAdapter(MarkerDetectorInterface):
    dictionary_name: str
    detector_parameters: Any | None = None

    def detect_markers(self, frame: CameraFrame) -> list[MarkerDetection]:
        raw_detections = self._detect_raw(frame)
        return [
            self._to_marker_detection(item, frame.timestamp)
            for item in raw_detections
        ]

    def _detect_raw(self, frame: CameraFrame) -> list[Any]:
        raise NotImplementedError("Bind cv2.aruco detection here.")

    def _to_marker_detection(self, raw_item: Any, timestamp: float) -> MarkerDetection:
        raise NotImplementedError("Convert OpenCV detection into MarkerDetection.")
