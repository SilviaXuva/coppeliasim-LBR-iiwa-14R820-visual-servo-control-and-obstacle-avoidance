from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.types import CycleResult, MetricsSnapshot, ScalarMetric
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


def test_scientific_metrics_persistence_regression() -> None:
    """
    REGRESSION TEST (5.2):
    Ensures that the scientific data (metrics, summary, run-id)
    is correctly serialized and not lost during persistence.
    """
    tmp_dir = (Path.cwd() / f".pytest_temp" / f"metrics_persistence_{uuid4().hex}").resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        repo = FileSystemResultsRepository(base_dir=str(tmp_dir))
        service = ExperimentService(results_repository=repo)

        # 1. Setup a realistic scientific result
        run_id = "test_scientific_001"

        metrics = MetricsSnapshot(
            scalar_metrics=(
                ScalarMetric(name="final_rmse", value=0.0012, unit="m"),
                ScalarMetric(name="settling_time", value=1.2, unit="s"),
            )
        )

        result = RunResult(
            run_id=run_id,
            success=True,
            num_cycles=2,
            summary={
                "experiment_name": "pbvs_accuracy_benchmark",
                "scenario_name": "static_target",
                "backend_name": "test_sim",
            },
            metrics=metrics,
            artifacts=(
                RunArtifact(
                    name="scientific_summary.json",
                    path=str(tmp_dir / "scientific_summary.json"),
                    kind="json",
                ),
            ),
            resolved_config={"gain": 0.5, "dt": 0.01},
            seed=42,
            start_time=100.0,
            end_time=105.0,
            cycle_results=(
                CycleResult(cycle_index=0, timestamp=100.0, success=True, events=("sensing: ok",)),
                CycleResult(cycle_index=1, timestamp=101.0, success=True, events=("sensing: ok",)),
            ),
        )

        (tmp_dir / "scientific_summary.json").write_text("{}", encoding="utf-8")

        # 2. Persist
        service.persist(result=result)

        # 3. Reload and Verify Filesystem state
        run_path = tmp_dir / run_id

        # Verify Metrics (CSV AND JSON)
        assert (run_path / "metrics.json").exists()
        assert (run_path / "metrics.csv").exists()

        with (run_path / "summary.json").open("r") as f:
            summary = json.load(f)
            assert summary["run_id"] == run_id
            assert summary["success"] is True
            assert summary["duration"] == 5.0

        with (run_path / "metrics.json").open("r") as f:
            metrics_payload = json.load(f)
            assert metrics_payload["scalar_metrics"][0]["name"] == "final_rmse"
            assert metrics_payload["scalar_metrics"][0]["value"] == 0.0012

        # Verify Logs (Entrega 4 traceability)
        with (run_path / "logs" / "run.log").open("r") as f:
            log_content = f.read()
            assert "seed=42" in log_content
            assert "last_cycle_index=1" in log_content
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
