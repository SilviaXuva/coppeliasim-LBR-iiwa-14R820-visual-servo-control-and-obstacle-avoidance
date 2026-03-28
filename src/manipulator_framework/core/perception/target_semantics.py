from __future__ import annotations

from enum import Enum


class ObservationType(str, Enum):
    MARKER = "marker"
    PERSON = "person"
    OBJECT = "object"
    UNKNOWN = "unknown"


class SemanticLabel(str, Enum):
    HUMAN = "human"
    FIDUCIAL_MARKER = "fiducial_marker"
    GENERIC_OBJECT = "generic_object"
    UNKNOWN = "unknown"
