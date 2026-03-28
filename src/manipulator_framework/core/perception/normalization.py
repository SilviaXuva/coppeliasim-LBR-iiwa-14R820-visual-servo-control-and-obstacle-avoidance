from __future__ import annotations

from manipulator_framework.core.types import Detection2D, MarkerDetection, PersonDetection
from .observation_models import SemanticObservation
from .target_semantics import ObservationType, SemanticLabel


def normalize_marker_detection(
    detection: MarkerDetection,
    source: str = "marker_detector",
) -> SemanticObservation:
    return SemanticObservation(
        observation_id=f"marker:{detection.marker_id}:{detection.timestamp}",
        observation_type=ObservationType.MARKER,
        semantic_label=SemanticLabel.FIDUCIAL_MARKER,
        confidence=detection.detection.confidence,
        source=source,
        detection_2d=detection.detection,
        marker_detection=detection,
        pose_hint=detection.pose_camera_frame,
        timestamp=detection.timestamp,
    )


def normalize_person_detection(
    detection: PersonDetection,
    source: str = "person_detector",
) -> SemanticObservation:
    return SemanticObservation(
        observation_id=f"person:{detection.person_id_hint or 'unknown'}:{detection.timestamp}",
        observation_type=ObservationType.PERSON,
        semantic_label=SemanticLabel.HUMAN,
        confidence=detection.detection.confidence,
        source=source,
        detection_2d=detection.detection,
        person_detection=detection,
        timestamp=detection.timestamp,
    )


def normalize_object_detection(
    detection: Detection2D,
    source: str = "object_detector",
) -> SemanticObservation:
    return SemanticObservation(
        observation_id=f"object:{detection.class_name or 'unknown'}:{detection.timestamp}",
        observation_type=ObservationType.OBJECT,
        semantic_label=SemanticLabel.GENERIC_OBJECT,
        confidence=detection.confidence,
        source=source,
        detection_2d=detection,
        timestamp=detection.timestamp,
    )
