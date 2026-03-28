from __future__ import annotations

from dataclasses import dataclass, field

from manipulator_framework.core.types import Detection2D, MarkerDetection, PersonDetection, Pose3D
from .target_semantics import ObservationType, SemanticLabel


@dataclass(frozen=True)
class SemanticObservation:
    """
    Canonical semantic observation representation used by the core.

    This is the internal representation after adapter outputs are normalized.
    """
    observation_id: str
    observation_type: ObservationType
    semantic_label: SemanticLabel
    confidence: float
    source: str
    detection_2d: Detection2D | None = None
    marker_detection: MarkerDetection | None = None
    person_detection: PersonDetection | None = None
    pose_hint: Pose3D | None = None
    timestamp: float = 0.0
