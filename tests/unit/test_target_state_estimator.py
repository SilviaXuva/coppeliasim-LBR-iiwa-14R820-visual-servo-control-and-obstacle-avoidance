from __future__ import annotations

from manipulator_framework.core.perception import normalize_person_detection
from manipulator_framework.core.estimation import SemanticTargetStateEstimator
from manipulator_framework.core.types import Detection2D, PersonDetection, TargetType


def test_person_observation_becomes_person_target() -> None:
    detection = Detection2D(
        bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
        confidence=0.9,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=2.0,
    )

    person = PersonDetection(
        detection=detection,
        person_id_hint="p1",
        timestamp=2.0,
    )

    observation = normalize_person_detection(person)
    estimator = SemanticTargetStateEstimator()
    estimate = estimator.estimate(observation)

    assert estimate.target.target_type is TargetType.PERSON
    assert estimate.target.latest_detection is detection
