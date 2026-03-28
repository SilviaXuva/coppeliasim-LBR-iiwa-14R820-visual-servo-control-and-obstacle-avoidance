from __future__ import annotations

from abc import ABC, abstractmethod


class ClockInterface(ABC):
    """Abstract time source for simulation, real-time or replay."""

    @abstractmethod
    def now(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def dt(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def sleep_until(self, timestamp: float) -> None:
        raise NotImplementedError
