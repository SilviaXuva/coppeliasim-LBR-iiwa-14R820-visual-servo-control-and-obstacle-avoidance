from __future__ import annotations

from .observation_models import SemanticObservation
from .target_semantics import ObservationType


def is_marker_observation(observation: SemanticObservation) -> bool:
    return observation.observation_type is ObservationType.MARKER


def is_person_observation(observation: SemanticObservation) -> bool:
    return observation.observation_type is ObservationType.PERSON


def is_object_observation(observation: SemanticObservation) -> bool:
    return observation.observation_type is ObservationType.OBJECT
