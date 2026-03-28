from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExecutionEngineInterface(ABC):
    """Pipeline execution boundary."""

    @abstractmethod
    def step(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def run(self, num_cycles: int = 1) -> tuple[CycleResult, ...]:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
