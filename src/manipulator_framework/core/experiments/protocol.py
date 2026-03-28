from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .scenario_definition import ScenarioDefinition


@dataclass(frozen=True)
class ExperimentProtocol:
    """
    Reproducible experiment definition.
    """
    name: str
    scenario: ScenarioDefinition
    repetitions: int
    seeds: tuple[int, ...]
    compared_methods: tuple[str, ...]
    resolved_config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.repetitions <= 0:
            raise ValueError("repetitions must be positive.")
        if len(self.seeds) != self.repetitions:
            raise ValueError("seeds length must match repetitions.")
        if not self.compared_methods:
            raise ValueError("compared_methods cannot be empty.")
