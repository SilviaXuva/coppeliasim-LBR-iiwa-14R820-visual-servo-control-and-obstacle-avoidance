from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

_LOGGER_NAMESPACE = "manipulator_framework"
_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


@dataclass(slots=True)
class LoggingConfig:
    level: str | int | None = None
    log_to_console: bool | None = None
    log_to_file: bool | None = None
    log_file_path: str | Path | None = None


_current_config = LoggingConfig(
    level="INFO",
    log_to_console=True,
    log_file_path=None,
)


def setup_logging(config: LoggingConfig | None = None) -> logging.Logger:
    global _current_config

    resolved_config = _merge_config(config)
    logger = logging.getLogger(_LOGGER_NAMESPACE)
    logger.setLevel(_resolve_level(resolved_config.level))
    logger.propagate = False

    for handler in list(logger.handlers):
        if getattr(handler, "_manipulator_framework_handler", False):
            logger.removeHandler(handler)
            handler.close()

    formatter = logging.Formatter(_LOG_FORMAT)

    if resolved_config.log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler._manipulator_framework_handler = True  # type: ignore[attr-defined]
        logger.addHandler(console_handler)

    if resolved_config.log_file_path is not None:
        log_path = Path(resolved_config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler._manipulator_framework_handler = True  # type: ignore[attr-defined]
        logger.addHandler(file_handler)

    _current_config = resolved_config
    return logger


def get_logger(name: str) -> logging.Logger:
    if name == _LOGGER_NAMESPACE or name.startswith(f"{_LOGGER_NAMESPACE}."):
        return logging.getLogger(name)
    return logging.getLogger(name)


def _merge_config(config: LoggingConfig | None) -> LoggingConfig:
    if config is None:
        return LoggingConfig(
            level=_current_config.level,
            log_to_console=_current_config.log_to_console,
            log_file_path=_current_config.log_file_path,
        )
    return LoggingConfig(
        level=_current_config.level if config.level is None else config.level,
        log_to_console=(
            _current_config.log_to_console
            if config.log_to_console is None
            else bool(config.log_to_console)
        ),
        log_to_file=_resolve_log_to_file(config),
        log_file_path=_resolve_log_file_path(config),
    )


def _resolve_level(level: str | int | None) -> int:
    if isinstance(level, int):
        return level
    if level is None:
        return logging.INFO
    normalized = str(level).upper()
    resolved = logging.getLevelName(normalized)
    if isinstance(resolved, int):
        return resolved
    raise ValueError(
        "`level` must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
    )


def _resolve_log_to_file(config: LoggingConfig) -> bool:
    if config.log_to_file is not None:
        return bool(config.log_to_file)
    return _current_config.log_file_path is not None


def _resolve_log_file_path(config: LoggingConfig) -> str | Path | None:
    if config.log_to_file is False:
        return None
    if config.log_file_path is not None:
        return config.log_file_path
    return _current_config.log_file_path
