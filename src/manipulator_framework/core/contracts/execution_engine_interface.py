from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from typing import TYPE_CHECKING

from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.types import CycleResult

if TYPE_CHECKING:
    from manipulator_framework.core.runtime.pipeline import RuntimePipeline


class ExecutionEngineInterface(ABC):
    """
    Pipeline execution boundary contract.
    Ensures a single, official cycle result format for all simulations and runs.
    """

    @abstractmethod
    def set_pipeline(self, pipeline: RuntimePipeline) -> None:
        """Inject a runtime pipeline for execution."""
        raise NotImplementedError

    @abstractmethod
    def step(self) -> CycleResult:
        """Execute a single cycle and return its canonical result."""
        raise NotImplementedError

    @abstractmethod
    def run(
        self,
        *,
        run_id: str,
        resolved_config: dict[str, Any],
        seed: int,
        num_cycles: int = 1,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> RunResult:
        """Execute multiple cycles and return the canonical RunResult."""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state (like cycle index)."""
        raise NotImplementedError
