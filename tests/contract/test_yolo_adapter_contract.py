from __future__ import annotations

from manipulator_framework.adapters.vision.yolo.yolo_ultralytics_adapter import YoloUltralyticsAdapter
from manipulator_framework.core.contracts import PersonDetectorInterface


def test_yolo_adapter_implements_person_detector_interface() -> None:
    adapter = YoloUltralyticsAdapter(model=object())
    assert isinstance(adapter, PersonDetectorInterface)
