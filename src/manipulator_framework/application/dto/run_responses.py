from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.experiments import RunResult


@dataclass(frozen=True)
class RunResponse:
    run_result: RunResult


@dataclass(frozen=True)
class BenchmarkResponse:
    summary: dict[str, tuple[RunResult, ...]]
