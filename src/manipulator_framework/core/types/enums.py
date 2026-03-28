from __future__ import annotations

from enum import Enum


class CommandMode(str, Enum):
    POSITION = "position"
    VELOCITY = "velocity"
    TORQUE = "torque"


class TargetType(str, Enum):
    MARKER = "marker"
    PERSON = "person"
    OBJECT = "object"
    UNKNOWN = "unknown"


class TrackingStatus(str, Enum):
    TENTATIVE = "tentative"
    TRACKED = "tracked"
    LOST = "lost"
