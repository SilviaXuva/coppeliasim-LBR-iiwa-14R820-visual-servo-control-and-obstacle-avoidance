from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.types import Pose3D, TrackedTarget


@dataclass(frozen=True)
class PoseEstimate:
    pose: Pose3D
    confidence: float
    method: str
    timestamp: float = 0.0


@dataclass(frozen=True)
class TargetStateEstimate:
    target: TrackedTarget
    confidence: float
    method: str
    timestamp: float = 0.0
