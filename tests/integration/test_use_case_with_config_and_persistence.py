from __future__ import annotations

from pathlib import Path

from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric, TimeSeriesSample
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader
from manipulator_framework.infrastructure.logging.run_logger import RunLogger
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)
from manipulator_framework.infrastructure.utils.seeds import set_global_seed


class FakeUseCase:
    def execute(self, config: dict) -> dict:
        return {
            "metrics_series": [
                {"t": 0.0, "tracking_error": 0.20},
                {"t": 0.1, "tracking_error": 0.12},
            ],
            "artifact_text": "integration test artifact",
            "summary": {
                "success": True,
                "steps_executed": config["runtime"]["max_steps"],
            },
        }


def test_load_config_execute_and_persist_flow(tmp_path: Path) -> None:
    config_file = tmp_path / "experiment.yaml"
    config_file.write_text(
        """
app:
  name: manipulator_framework
  mode: experiment

runtime:
  dt: 0.02
  max_steps: 5

logging:
  level: INFO
  save_to_file: true

results:
  base_dir: PLACEHOLDER

experiment:
  name: integration_run
  seed: 123
  tags: [integration]
""".strip(),
        encoding="utf-8",
    )

    config_text = config_file.read_text(encoding="utf-8").replace(
        "PLACEHOLDER", str(tmp_path / "runs").replace("\\", "/")
    )
    config_file.write_text(config_text, encoding="utf-8")

    loader = YAMLConfigurationLoader()
    raw_config = loader.load(str(config_file))
    config = loader.resolve(raw_config)

    run_id = "integration_run_001"
    set_global_seed(config["experiment"]["seed"])

    repository = FileSystemResultsRepository(base_dir=config["results"]["base_dir"])
    logger = RunLogger(
        run_id=run_id,
        log_dir=str(Path(config["results"]["base_dir"]) / run_id / "logs"),
        level=config["logging"]["level"],
    )

    logger.info("Starting integration test flow.", run_id=run_id)

    use_case = FakeUseCase()
    output = use_case.execute(config)

    artifact_file = tmp_path / "artifact.txt"
    artifact_file.write_text(output["artifact_text"], encoding="utf-8")

    tracking_series = tuple(
        TimeSeriesSample(
            t=float(sample["t"]),
            values={"tracking_error": float(sample["tracking_error"])},
        )
        for sample in output["metrics_series"]
    )

    result = RunResult(
        run_id=run_id,
        success=output["summary"]["success"],
        num_cycles=config["runtime"]["max_steps"],
        summary={
            "experiment_name": config["experiment"]["name"],
            "scenario_name": "integration_scenario",
            "backend_name": "mock",
            "steps_executed": output["summary"]["steps_executed"],
        },
        metrics=MetricsSnapshot(
            scalar_metrics=(
                ScalarMetric(name="success_rate", value=1.0, unit="ratio"),
            ),
            series={"tracking_error_series": tracking_series},
        ),
        artifacts=(
            RunArtifact(name="artifact.txt", path=str(artifact_file), kind="text"),
        ),
        resolved_config=config,
        seed=config["experiment"]["seed"],
        start_time=0.0,
        end_time=1.0,
    )

    repository.save_run(result)

    run_dir = Path(config["results"]["base_dir"]) / run_id
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "tracking_error_series.json").exists()
    assert (run_dir / "artifacts" / "artifact.txt").exists()
    assert (run_dir / "logs" / "run.log").exists()
