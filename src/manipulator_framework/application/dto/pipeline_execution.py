from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.core.runtime import CycleResult


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Explicit execution plan produced by the application layer.
    """
    duration: float
    dt: float
    num_cycles: int


@dataclass(frozen=True)
class PipelineExecutionSummary:
    """
    Aggregated runtime execution summary returned by application services.
    """
    plan: ExecutionPlan
    cycle_results: tuple[CycleResult, ...]
    started_at: float
    finished_at: float

    @property
    def success(self) -> bool:
        return bool(self.cycle_results) and all(result.success for result in self.cycle_results)

    @property
    def final_cycle_result(self) -> CycleResult:
        if not self.cycle_results:
            raise ValueError("cycle_results cannot be empty.")
        return self.cycle_results[-1]

    def cycle_success_flags(self) -> list[bool]:
        return [result.success for result in self.cycle_results]

    def runtime_series(self) -> list[dict[str, Any]]:
        samples: list[dict[str, Any]] = []
        for result in self.cycle_results:
            samples.append(
                {
                    "t": result.timestamp,
                    "cycle_index": result.cycle_index,
                    "success": 1.0 if result.success else 0.0,
                    "num_events": float(len(result.events)),
                    "num_errors": float(len(result.errors)),
                }
            )
        return samples
