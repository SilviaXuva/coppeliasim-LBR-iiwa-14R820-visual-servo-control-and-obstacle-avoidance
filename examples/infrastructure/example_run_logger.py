from __future__ import annotations

from manipulator_framework.infrastructure.logging.run_logger import RunLogger


def main() -> None:
    logger = RunLogger(
        run_id="example_run_001",
        log_dir="experiments/runs/example_run_001/logs",
        level="INFO",
    )

    logger.info("Run started.", step="bootstrap")
    logger.info("Configuration loaded.", source="configs/app/experiment.yaml")
    logger.warning("This is a synthetic example.")
    logger.info("Run finished.", status="ok")


if __name__ == "__main__":
    main()
