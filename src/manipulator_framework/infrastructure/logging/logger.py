from __future__ import annotations

import logging
from typing import Any


def _format_message(message: str, context: dict[str, Any]) -> str:
    if not context:
        return message
    context_str = " ".join(f"{key}={value}" for key, value in context.items())
    return f"{message} | {context_str}"


class StructuredLogger:
    """Thin wrapper around the standard logging module."""

    def __init__(self, name: str, level: str = "INFO") -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

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
