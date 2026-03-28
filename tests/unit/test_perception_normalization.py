from __future__ import annotations

from manipulator_framework.core.perception import normalize_object_detection, ObservationType
from manipulator_framework.core.types import Detection2D


def test_object_detection_is_normalized_to_semantic_observation() -> None:
    detection = Detection2D(
        bbox_xyxy=(10.0, 20.0, 30.0, 40.0),
        confidence=0.8,
        class_id=1,
        class_name="cube",
        image_size_wh=(640, 480),
        timestamp=1.0,
    )

    observation = normalize_object_detection(detection)

    assert observation.observation_type is ObservationType.OBJECT
    assert observation.detection_2d is detection
    assert observation.confidence == 0.8
