from __future__ import annotations

from pathlib import Path

from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


class FakeExperimentResult:
    """
    Placeholder local object used only for this example.

    Replace it with the real ExperimentResult from core/types
    if your current dataclass already exposes 'run_id'.
    """

    def __init__(self, run_id: str, metadata: dict, summary: dict) -> None:
        self.run_id = run_id
        self.metadata = metadata
        self.summary = summary


def main() -> None:
    repository = FileSystemResultsRepository(base_dir="experiments/runs")

    artifact_path = Path("experiments/tmp_artifact.txt")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("temporary artifact", encoding="utf-8")

    result = FakeExperimentResult(
        run_id="example_run_002",
        metadata={"seed": 123, "scenario": "synthetic"},
        summary={"success": True},
    )

    repository.save_result(result)  # replace with real ExperimentResult when already available
    repository.save_timeseries(
        run_id="example_run_002",
        series_name="latency_series",
        samples=[
            {"t": 0.0, "latency_ms": 4.2},
            {"t": 0.1, "latency_ms": 4.6},
            {"t": 0.2, "latency_ms": 4.1},
        ],
    )
    repository.save_artifact(
        run_id="example_run_002",
        artifact_name="tmp_artifact.txt",
        artifact_path=str(artifact_path),
    )

    print("Repository example completed.")


if __name__ == "__main__":
    main()
