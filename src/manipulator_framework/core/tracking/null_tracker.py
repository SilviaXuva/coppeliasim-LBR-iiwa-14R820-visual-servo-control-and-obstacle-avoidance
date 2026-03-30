from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import TrackerInterface
from manipulator_framework.core.types import TrackedTarget


@dataclass
class NullTracker(TrackerInterface):
    """
    Explicit no-op tracker for scenarios where temporal tracking is out of scope.
    """

    def update(self, detections: list[TrackedTarget], timestamp: float) -> list[TrackedTarget]:
        return list(detections)

    def reset(self) -> None:
        return None
