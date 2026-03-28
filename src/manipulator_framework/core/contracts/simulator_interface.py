from __future__ import annotations

from abc import ABC, abstractmethod


class SimulatorInterface(ABC):
    """Simulation runtime boundary."""

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def step(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
