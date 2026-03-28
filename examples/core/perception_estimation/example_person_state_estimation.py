from __future__ import annotations

import numpy as np

from manipulator_framework.core.perception import normalize_person_detection
from manipulator_framework.core.estimation import SemanticTargetStateEstimator
from manipulator_framework.core.types import Detection2D, PersonDetection


def main() -> None:
    detection_2d = Detection2D(
        bbox_xyxy=(150.0, 80.0, 260.0, 320.0),
        confidence=0.91,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=2.0,
    )

    person_detection = PersonDetection(
        detection=detection_2d,
        keypoints_uv=((180.0, 90.0), (175.0, 130.0), (190.0, 130.0)),
        person_id_hint="candidate_001",
        timestamp=2.0,
    )

    observation = normalize_person_detection(person_detection)
    estimator = SemanticTargetStateEstimator()
    estimate = estimator.estimate(observation)

    print(observation)
    print(estimate)
    print(estimate.target.to_dict())


if __name__ == "__main__":
    main()
