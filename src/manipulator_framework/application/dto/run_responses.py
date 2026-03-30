from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.runtime import CycleResult


@dataclass(frozen=True)
class RunResponse:
    run_result: RunResult

    @property
    def cycle_results(self) -> tuple[CycleResult, ...]:
        return self.run_result.cycle_results

    @property
    def cycle_result(self) -> CycleResult:
        if not self.run_result.cycle_results:
            raise ValueError("run_result.cycle_results cannot be empty.")
        return self.run_result.cycle_results[-1]


@dataclass(frozen=True)
class BenchmarkResponse:
    summary: dict[str, tuple[RunResult, ...]]


@dataclass(frozen=True)
class ProtocolRunSummary:
    run_id: str
    success: bool
    final_visual_error: float | None
    minimum_clearance: float | None


@dataclass(frozen=True)
class RunPBVSProtocolResponse:
    protocol_name: str
    repetitions: int
    run_ids: tuple[str, ...]
    runs: tuple[ProtocolRunSummary, ...]
