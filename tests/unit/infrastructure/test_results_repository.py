from __future__ import annotations

from pathlib import Path

from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


def test_results_repository_saves_canonical_run_result(tmp_path: Path) -> None:
    repository = FileSystemResultsRepository(base_dir=str(tmp_path))
    run_id = "run_001"

    result = RunResult(
        run_id=run_id,
        success=True,
        num_cycles=3,
        summary={
            "experiment_name": "run_joint_trajectory",
            "scenario_name": "synthetic_joint_trajectory",
            "backend_name": "mock",
        },
        metrics=MetricsSnapshot(
            scalar_metrics=(
                ScalarMetric(name="success_rate", value=1.0, unit="ratio"),
            ),
        ),
        artifacts=(
            RunArtifact(name="artifact.txt", path=str(tmp_path / "artifact.txt"), kind="text"),
        ),
        resolved_config={"runtime": {"dt": 0.01}},
        seed=123,
        start_time=0.0,
        end_time=1.0,
    )

    artifact_source = tmp_path / "artifact.txt"
    artifact_source.write_text("artifact payload", encoding="utf-8")

    repository.save_run(result)

    run_dir = tmp_path / run_id
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "artifacts" / "artifact.txt").exists()


def test_results_repository_guarantees_minimum_run_files_contract(tmp_path: Path) -> None:
    repository = FileSystemResultsRepository(base_dir=str(tmp_path / "experiments" / "runs"))
    run_id = "run_contract_001"

    result = RunResult(
        run_id=run_id,
        success=False,
        num_cycles=0,
        summary={},
        metrics=MetricsSnapshot(scalar_metrics=()),
        resolved_config={},
    )

    repository.save_run(result)

    run_dir = tmp_path / "experiments" / "runs" / run_id
    for filename in FileSystemResultsRepository.REQUIRED_RUN_FILES:
        assert (run_dir / filename).exists()
