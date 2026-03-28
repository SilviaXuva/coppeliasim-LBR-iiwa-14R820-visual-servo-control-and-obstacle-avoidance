from __future__ import annotations

from pathlib import Path

from manipulator_framework.infrastructure.logging.run_logger import RunLogger


def test_run_logger_creates_log_file(tmp_path: Path) -> None:
    run_id = "run_logger_test"
    log_dir = tmp_path / "logs"

    logger = RunLogger(
        run_id=run_id,
        log_dir=str(log_dir),
        level="INFO",
    )

    logger.info("Test message.", step="unit_test")

    log_file = log_dir / "run.log"
    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")
    assert "Test message." in content
    assert "step=unit_test" in content
