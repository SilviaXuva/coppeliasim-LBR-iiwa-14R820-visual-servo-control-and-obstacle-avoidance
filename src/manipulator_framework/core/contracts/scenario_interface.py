from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ScenarioInterface(ABC):
    """Scenario definition contract."""

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def build(self) -> dict[str, Any]:
        """Return scenario description/components placeholders."""
        raise NotImplementedError
