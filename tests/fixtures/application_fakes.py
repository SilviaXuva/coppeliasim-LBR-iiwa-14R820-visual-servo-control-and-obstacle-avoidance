from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.core.contracts import (
    ClockInterface,
    ExecutionEngineInterface,
    ResultsRepositoryInterface,
)
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.runtime import CycleResult, StepResult


class FakeClock(ClockInterface):
    """
    Simple deterministic clock for examples and tests.
    """

    def __init__(self, start_time: float = 0.0, step_dt: float = 0.1) -> None:
        self._now = float(start_time)
        self._dt = float(step_dt)

    def now(self) -> float:
        return self._now

    def dt(self) -> float:
        return self._dt

    def sleep_until(self, timestamp: float) -> None:
        if timestamp < self._now:
            raise ValueError("timestamp cannot be earlier than current fake clock time.")
        self._now = float(timestamp)

    def tick(self) -> float:
        """
        Advance the fake clock by one dt step.
        """
        self._now += self._dt
        return self._now


class FakeExecutionEngine(ExecutionEngineInterface):
    """
    Fake execution engine aligned with the real engine contract.
    """

    def __init__(
        self,
        *,
        success: bool = True,
        step_names: tuple[str, ...] = ("sensing", "planning", "control"),
        timestamp: float = 0.0,
        failure_step_index: int | None = None,
    ) -> None:
        self._cycle = 0
        self._success = bool(success)
        self._step_names = tuple(step_names)
        self._timestamp = float(timestamp)
        self._failure_step_index = failure_step_index

    def step(self) -> CycleResult:
        step_results: list[StepResult] = []

        for index, step_name in enumerate(self._step_names):
            step_success = self._success
            if self._failure_step_index is not None and index == self._failure_step_index:
                step_success = False

            step_results.append(
                StepResult(
                    step_name=step_name,
                    success=step_success,
                    message=(
                        f"{step_name} completed."
                        if step_success
                        else f"{step_name} failed."
                    ),
                    timestamp=self._timestamp,
                )
            )

            if not step_success:
                break

        overall_success = all(item.success for item in step_results)
        result = CycleResult(
            cycle_index=self._cycle,
            success=overall_success,
            step_results=tuple(step_results),
            timestamp=self._timestamp,
            message=(
                "Fake cycle completed."
                if overall_success
                else "Fake cycle failed."
            ),
        )
        self._cycle += 1
        return result

    def run(self, num_cycles: int = 1) -> tuple[CycleResult, ...]:
        if num_cycles <= 0:
            raise ValueError("num_cycles must be greater than zero.")

        results: list[CycleResult] = []
        for _ in range(num_cycles):
            results.append(self.step())
        return tuple(results)

    def reset(self) -> None:
        self._cycle = 0


@dataclass
class InMemoryResultsRepository(ResultsRepositoryInterface):
    """
    In-memory repository aligned with the consolidated RunResult contract.
    """

    saved_results: list[RunResult] = field(default_factory=list)
    saved_timeseries: dict[str, dict[str, list[dict[str, Any]]]] = field(default_factory=dict)
    saved_artifacts: dict[str, dict[str, str]] = field(default_factory=dict)

    def save_result(self, result: RunResult) -> None:
        self.saved_results.append(result)

    def save_timeseries(
        self,
        run_id: str,
        series_name: str,
        samples: list[dict[str, Any]],
    ) -> None:
        if run_id not in self.saved_timeseries:
            self.saved_timeseries[run_id] = {}
        self.saved_timeseries[run_id][series_name] = list(samples)

    def save_artifact(
        self,
        run_id: str,
        artifact_name: str,
        artifact_path: str,
    ) -> None:
        if run_id not in self.saved_artifacts:
            self.saved_artifacts[run_id] = {}
        self.saved_artifacts[run_id][artifact_name] = artifact_path
