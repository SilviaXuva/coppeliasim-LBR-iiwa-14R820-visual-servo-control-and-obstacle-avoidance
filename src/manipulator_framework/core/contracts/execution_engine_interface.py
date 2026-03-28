from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExecutionEngineInterface(ABC):
    """Pipeline execution boundary."""

    @abstractmethod
    def step(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def run(self, steps: int | None = None) -> dict[str, Any]:
        raise NotImplementedError
