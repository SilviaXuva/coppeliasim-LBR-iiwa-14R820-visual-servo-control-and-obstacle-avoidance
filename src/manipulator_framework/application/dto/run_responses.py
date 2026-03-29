from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.dto.pipeline_execution import ExecutionPlan
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.runtime import CycleResult


@dataclass(frozen=True)
class RunResponse:
    execution_plan: ExecutionPlan
    cycle_results: tuple[CycleResult, ...]
    cycle_result: CycleResult
    run_result: RunResult


@dataclass(frozen=True)
class BenchmarkResponse:
    summary: dict[str, tuple[RunResult, ...]]
