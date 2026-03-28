from __future__ import annotations

from pathlib import Path

from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader
from manipulator_framework.infrastructure.logging.run_logger import RunLogger
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)
from manipulator_framework.infrastructure.utils.seeds import set_global_seed


class FakeExperimentResult:
    """
    Placeholder local object.

    Replace this with the real ExperimentResult from core/types
    after aligning the constructor with your current dataclass.
    """

    def __init__(self, run_id: str, metadata: dict, summary: dict) -> None:
        self.run_id = run_id
        self.metadata = metadata
        self.summary = summary


class FakeUseCase:
    """Minimal fake use case only for infrastructure validation."""

    def execute(self, config: dict) -> dict:
        return {
            "metrics_series": [
                {"t": 0.0, "tracking_error": 0.20},
                {"t": 0.1, "tracking_error": 0.14},
                {"t": 0.2, "tracking_error": 0.08},
            ],
            "artifact_text": "Fake execution report.",
            "summary": {
                "success": True,
                "steps_executed": config["runtime"]["max_steps"],
            },
        }


def main() -> None:
    loader = YAMLConfigurationLoader()
    repository = FileSystemResultsRepository(base_dir="experiments/runs")

    raw_config = loader.load("configs/app/experiment.yaml")
    config = loader.resolve(raw_config)

    run_id = "example_run_003"
    set_global_seed(config["experiment"]["seed"])

    logger = RunLogger(
        run_id=run_id,
        log_dir=f"experiments/runs/{run_id}/logs",
        level=config["logging"]["level"],
    )

    logger.info("Starting configured execution.", run_id=run_id)
    logger.info("Configuration resolved.", app_mode=config["app"]["mode"])

    use_case = FakeUseCase()
    output = use_case.execute(config)

    artifact_path = Path("experiments/tmp_execution_report.txt")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(output["artifact_text"], encoding="utf-8")

    result = FakeExperimentResult(
        run_id=run_id,
        metadata={
            "seed": config["experiment"]["seed"],
            "experiment_name": config["experiment"]["name"],
            "tags": config["experiment"]["tags"],
        },
        summary=output["summary"],
    )

    repository.save_result(result)  # replace with real ExperimentResult when available
    repository.save_timeseries(run_id, "tracking_error_series", output["metrics_series"])
    repository.save_artifact(run_id, "execution_report.txt", str(artifact_path))

    logger.info("Execution finished.", success=output["summary"]["success"])
    print(f"Completed run: {run_id}")


if __name__ == "__main__":
    main()
