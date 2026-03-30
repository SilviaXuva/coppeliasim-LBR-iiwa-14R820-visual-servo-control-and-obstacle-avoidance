from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import PersonDetectorInterface
from manipulator_framework.core.types import CameraFrame, Detection2D, PersonDetection


@dataclass
class YoloUltralyticsAdapter(PersonDetectorInterface):
    """
    Ultralytics YOLO adapter specialized for person detection.
    """
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
        if hasattr(self.model, "predict"):
            return list(
                self.model.predict(
                    frame.image,
                    conf=self.confidence_threshold,
                    verbose=False,
                )
            )
        if callable(self.model):
            return list(self.model(frame.image))
        raise TypeError("YOLO model must be callable or expose a predict(...) method.")

    def _to_person_detection(self, raw_item: Any, timestamp: float) -> PersonDetection | None:
        names = self._extract_names(raw_item)
        image_h, image_w = self._extract_image_size(raw_item)

        for box_item in self._iterate_boxes(raw_item):
            class_id = int(box_item["class_id"]) if box_item["class_id"] is not None else None
            class_name = self._resolve_class_name(names, class_id, box_item["class_name"])

            if not self._is_person(class_id, class_name):
                continue

            confidence = float(box_item["confidence"])
            if confidence < self.confidence_threshold:
                continue

            keypoints_uv = self._extract_keypoints(raw_item, box_item["index"])

            return PersonDetection(
                detection=Detection2D(
                    bbox_xyxy=tuple(float(v) for v in box_item["bbox_xyxy"]),
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                    image_size_wh=(image_w, image_h) if image_w and image_h else None,
                    timestamp=timestamp,
                ),
                keypoints_uv=keypoints_uv,
                person_id_hint=None,
                timestamp=timestamp,
            )

        return None

    def _iterate_boxes(self, raw_item: Any) -> list[dict[str, Any]]:
        boxes = getattr(raw_item, "boxes", None)
        if boxes is None:
            return []

        xyxy = self._to_numpy(getattr(boxes, "xyxy", []))
        conf = self._to_numpy(getattr(boxes, "conf", []))
        cls = self._to_numpy(getattr(boxes, "cls", []))

        items: list[dict[str, Any]] = []
        for index in range(len(xyxy)):
            items.append(
                {
                    "index": index,
                    "bbox_xyxy": xyxy[index].reshape(4),
                    "confidence": float(conf[index]) if len(conf) > index else 0.0,
                    "class_id": int(cls[index]) if len(cls) > index else None,
                    "class_name": None,
                }
            )
        return items

    def _extract_keypoints(self, raw_item: Any, index: int) -> tuple[tuple[float, float], ...]:
        keypoints = getattr(raw_item, "keypoints", None)
        if keypoints is None:
            return ()

        xy = getattr(keypoints, "xy", None)
        if xy is None:
            return ()

        xy_np = self._to_numpy(xy)
        if xy_np.ndim != 3 or len(xy_np) <= index:
            return ()

        return tuple((float(x), float(y)) for x, y in xy_np[index])

    def _extract_names(self, raw_item: Any) -> dict[int, str]:
        names = getattr(raw_item, "names", None)
        if isinstance(names, dict):
            return {int(k): str(v) for k, v in names.items()}
        return {}

    def _extract_image_size(self, raw_item: Any) -> tuple[int, int]:
        orig_shape = getattr(raw_item, "orig_shape", None)
        if orig_shape is None:
            return 0, 0
        return int(orig_shape[0]), int(orig_shape[1])

    def _resolve_class_name(
        self,
        names: dict[int, str],
        class_id: int | None,
        explicit_name: str | None,
    ) -> str | None:
        if explicit_name is not None:
            return explicit_name
        if class_id is None:
            return None
        return names.get(class_id)

    def _is_person(self, class_id: int | None, class_name: str | None) -> bool:
        if class_name is not None:
            return class_name.lower() == "person"
        return class_id == 0

    def _to_numpy(self, value: Any) -> np.ndarray:
        if hasattr(value, "cpu"):
            value = value.cpu()
        if hasattr(value, "numpy"):
            value = value.numpy()
        return np.asarray(value)


@dataclass
class YoloUltralyticsPersonDetectorAdapter(YoloUltralyticsAdapter):
    """
    Backward/semantic alias for the person-detection role in composition roots.
    """
