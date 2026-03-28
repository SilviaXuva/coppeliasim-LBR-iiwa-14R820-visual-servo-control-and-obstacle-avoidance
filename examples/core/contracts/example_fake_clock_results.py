from __future__ import annotations

from manipulator_framework.core.contracts import ClockInterface, ResultsRepositoryInterface
from manipulator_framework.core.types import ExperimentResult


class FakeClock(ClockInterface):
    def __init__(self) -> None:
        self._t = 0.0
        self._dt = 0.1

    def now(self) -> float:
        return self._t

    def dt(self) -> float:
        return self._dt

    def sleep_until(self, timestamp: float) -> None:
        self._t = timestamp


class InMemoryResultsRepository(ResultsRepositoryInterface):
    def __init__(self) -> None:
        self.results: list[ExperimentResult] = []
        self.timeseries: dict[str, list[dict]] = {}
        self.artifacts: dict[str, dict[str, str]] = {}

    def save_result(self, result: ExperimentResult) -> None:
        self.results.append(result)

    def save_timeseries(self, run_id: str, series_name: str, samples: list[dict]) -> None:
        key = f"{run_id}:{series_name}"
        self.timeseries[key] = samples

    def save_artifact(self, run_id: str, artifact_name: str, artifact_path: str) -> None:
        self.artifacts.setdefault(run_id, {})[artifact_name] = artifact_path


def main() -> None:
    clock = FakeClock()
    repo = InMemoryResultsRepository()

    clock.sleep_until(10.0)

    result = ExperimentResult(
        experiment_name="contract_test",
        run_id="run_contract_001",
        success=True,
        metrics={"final_error": 0.01},
        artifacts={},
        metadata={"backend": "fake"},
        started_at=0.0,
        finished_at=clock.now(),
    )

    repo.save_result(result)
    repo.save_timeseries("run_contract_001", "joint_error", [{"t": 0.0, "e": 1.0}, {"t": 0.1, "e": 0.8}])
    repo.save_artifact("run_contract_001", "summary_json", "memory://summary.json")

    print(repo.results[0].to_dict())
    print(repo.timeseries)
    print(repo.artifacts)


if __name__ == "__main__":
    main()
