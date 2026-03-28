from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import Detection2D, TrackedTarget


class TrackerInterface(ABC):
    """Maintain temporal identity and state continuity."""

    @abstractmethod
    def update(self, detections: list[Detection2D], timestamp: float) -> list[TrackedTarget]:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
