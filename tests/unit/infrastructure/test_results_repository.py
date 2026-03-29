from __future__ import annotations

from pathlib import Path

from manipulator_framework.core.experiments import RunArtifact, RunResult, RunSchema
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


def test_results_repository_saves_canonical_run_result(tmp_path: Path) -> None:
    repository = FileSystemResultsRepository(base_dir=str(tmp_path))
    run_id = "run_001"

    result = RunResult(
        run_schema=RunSchema(
            run_id=run_id,
            experiment_name="run_joint_trajectory",
            scenario_name="synthetic_joint_trajectory",
            backend_name="mock",
            seed=123,
            resolved_config={"runtime": {"dt": 0.01}},
        ),
        metrics=MetricsSnapshot(
            scalar_metrics=(
                ScalarMetric(name="success_rate", value=1.0, unit="ratio"),
            ),
        ),
        artifacts=(
            RunArtifact(name="summary", path="experiments/runs/run_001/summary.json", kind="json"),
        ),
        success=True,
        started_at=0.0,
        finished_at=1.0,
        metadata={"controller": "pd"},
    )

    artifact_source = tmp_path / "artifact.txt"
    artifact_source.write_text("artifact payload", encoding="utf-8")

    repository.save_result(result)
    repository.save_artifact(
        run_id=run_id,
        artifact_name="artifact.txt",
        artifact_path=str(artifact_source),
    )

    run_dir = tmp_path / run_id
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "artifacts" / "artifact.txt").exists()
