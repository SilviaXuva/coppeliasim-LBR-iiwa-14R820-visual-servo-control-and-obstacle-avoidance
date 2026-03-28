from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


@dataclass
class FakeExperimentResult:
    run_id: str
    metadata: dict[str, Any]
    summary: dict[str, Any]


def test_results_repository_saves_result_timeseries_and_artifact(tmp_path: Path) -> None:
    repository = FileSystemResultsRepository(base_dir=str(tmp_path))
    run_id = "run_001"

    result = FakeExperimentResult(
        run_id=run_id,
        metadata={"seed": 123},
        summary={"success": True},
    )

    artifact_source = tmp_path / "artifact.txt"
    artifact_source.write_text("artifact payload", encoding="utf-8")

    repository.save_result(result)
    repository.save_timeseries(
        run_id=run_id,
        series_name="latency_series",
        samples=[
            {"t": 0.0, "latency_ms": 4.2},
            {"t": 0.1, "latency_ms": 4.3},
        ],
    )
    repository.save_artifact(
        run_id=run_id,
        artifact_name="artifact.txt",
        artifact_path=str(artifact_source),
    )

    run_dir = tmp_path / run_id
    assert (run_dir / "result.json").exists()
    assert (run_dir / "latency_series.json").exists()
    assert (run_dir / "artifacts" / "artifact.txt").exists()
