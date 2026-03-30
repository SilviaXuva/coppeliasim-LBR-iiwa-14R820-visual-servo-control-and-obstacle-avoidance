from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import ObjectDetectorInterface
from manipulator_framework.core.types import CameraFrame, Detection2D


@dataclass
class YoloObjectAdapter(ObjectDetectorInterface):
    """
    Ultralytics YOLO adapter for generic object detections.

    By default, all classes are returned except those explicitly excluded.
    """
    model: Any
    confidence_threshold: float = 0.25
    excluded_class_names: tuple[str, ...] = field(default_factory=tuple)

    def detect_objects(self, frame: CameraFrame) -> list[Detection2D]:
        raw_results = self._infer(frame)
        detections: list[Detection2D] = []

        for raw_item in raw_results:
            names = self._extract_names(raw_item)
            image_h, image_w = self._extract_image_size(raw_item)

            for box_item in self._iterate_boxes(raw_item):
                class_id = int(box_item["class_id"]) if box_item["class_id"] is not None else None
                class_name = self._resolve_class_name(names, class_id)

                confidence = float(box_item["confidence"])
                if confidence < self.confidence_threshold:
                    continue

                if class_name is not None and class_name in self.excluded_class_names:
                    continue

                detections.append(
                    Detection2D(
                        bbox_xyxy=tuple(float(v) for v in box_item["bbox_xyxy"]),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                        image_size_wh=(image_w, image_h) if image_w and image_h else None,
                        timestamp=frame.timestamp,
                    )
                )

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
                    "bbox_xyxy": xyxy[index].reshape(4),
                    "confidence": float(conf[index]) if len(conf) > index else 0.0,
                    "class_id": int(cls[index]) if len(cls) > index else None,
                }
            )
        return items

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
    ) -> str | None:
        if class_id is None:
            return None
        return names.get(class_id)

    def _to_numpy(self, value: Any) -> np.ndarray:
        if hasattr(value, "cpu"):
            value = value.cpu()
        if hasattr(value, "numpy"):
            value = value.numpy()
        return np.asarray(value)
