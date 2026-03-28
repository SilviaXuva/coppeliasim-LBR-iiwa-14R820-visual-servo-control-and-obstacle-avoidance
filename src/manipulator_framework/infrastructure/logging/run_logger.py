from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from manipulator_framework.core.contracts.logger_interface import LoggerInterface


def _format_message(message: str, context: dict[str, Any]) -> str:
    if not context:
        return message
    context_str = " ".join(f"{key}={value}" for key, value in context.items())
    return f"{message} | {context_str}"


class RunLogger(LoggerInterface):
    """Run-scoped logger with file output support."""

    def __init__(self, run_id: str, log_dir: str, level: str = "INFO") -> None:
        self.run_id = run_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(f"run.{run_id}")
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self._logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(self.log_dir / "run.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def debug(self, message: str, **context: Any) -> None:
        self._logger.debug(_format_message(message, context))

    def info(self, message: str, **context: Any) -> None:
        self._logger.info(_format_message(message, context))

    def warning(self, message: str, **context: Any) -> None:
        self._logger.warning(_format_message(message, context))

    def error(self, message: str, **context: Any) -> None:
        self._logger.error(_format_message(message, context))

    def exception(self, message: str, **context: Any) -> None:
        self._logger.exception(_format_message(message, context))
