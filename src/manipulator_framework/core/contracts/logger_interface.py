from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoggerInterface(ABC):
    """Abstract logger for execution, experiment and infrastructure events."""

    @abstractmethod
    def debug(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def info(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def exception(self, message: str, **context: Any) -> None:
        raise NotImplementedError
