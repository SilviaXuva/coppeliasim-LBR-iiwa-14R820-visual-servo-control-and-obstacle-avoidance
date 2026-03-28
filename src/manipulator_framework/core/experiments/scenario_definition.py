from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScenarioDefinition:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
