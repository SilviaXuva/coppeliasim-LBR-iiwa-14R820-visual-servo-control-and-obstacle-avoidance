from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import TrackedTarget


class TrackerInterface(ABC):
    """Maintain temporal identity and state continuity."""

    @abstractmethod
    def update(self, observations: list[TrackedTarget], timestamp: float) -> list[TrackedTarget]:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
