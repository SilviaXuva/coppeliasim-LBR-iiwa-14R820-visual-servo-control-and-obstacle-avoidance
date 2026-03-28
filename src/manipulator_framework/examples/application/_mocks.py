from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.core.contracts import (
    ClockInterface,
    ExecutionEngineInterface,
    ResultsRepositoryInterface,
)
from manipulator_framework.core.types import ExperimentResult


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
    Minimal fake execution engine for application-layer examples.
    """

    def __init__(self) -> None:
        self._cycle = 0

    def step(self) -> dict[str, Any]:
        result = {
            "cycle_index": self._cycle,
            "success": True,
            "step_results": (
                {"step_name": "sensing", "success": True, "timestamp": 0.0},
                {"step_name": "planning", "success": True, "timestamp": 0.0},
                {"step_name": "control", "success": True, "timestamp": 0.0},
            ),
            "timestamp": 0.0,
            "message": "Fake cycle completed.",
        }
        self._cycle += 1
        return result

    def run(self, num_cycles: int = 1) -> tuple[dict[str, Any], ...]:
        if num_cycles < 0:
            raise ValueError("num_cycles must be non-negative.")

        results: list[dict[str, Any]] = []
        for _ in range(num_cycles):
            results.append(self.step())
        return tuple(results)

    def reset(self) -> None:
        self._cycle = 0


@dataclass
class InMemoryResultsRepository(ResultsRepositoryInterface):
    """
    In-memory repository for tests and examples.
    """

    saved_results: list[ExperimentResult] = field(default_factory=list)
    saved_timeseries: dict[str, dict[str, list[dict[str, Any]]]] = field(default_factory=dict)
    saved_artifacts: dict[str, dict[str, str]] = field(default_factory=dict)

    def save_result(self, result: ExperimentResult) -> None:
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
