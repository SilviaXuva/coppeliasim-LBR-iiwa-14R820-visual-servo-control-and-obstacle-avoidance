from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manipulator_framework.core.runtime.cycle_contract import CycleResult


class ExecutionEngineInterface(ABC):
    """Pipeline execution boundary."""

    @abstractmethod
    def step(self) -> "CycleResult":
        raise NotImplementedError

    @abstractmethod
    def run(self, num_cycles: int = 1) -> tuple["CycleResult", ...]:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
