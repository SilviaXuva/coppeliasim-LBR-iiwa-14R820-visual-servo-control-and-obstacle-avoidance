from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConfigurationInterface(ABC):
    """Load and resolve application or experiment configuration."""

    @abstractmethod
    def load(self, source: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def resolve(self, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
