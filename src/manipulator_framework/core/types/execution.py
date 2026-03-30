from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StepResult:
    """
    Result of a single pipeline step execution.
    """
    step_name: str
    success: bool
    message: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CycleResult:
    """
    Canonical result of one full runtime cycle.
    Contains only cycle-level data.
    """
    cycle_index: int
    timestamp: float = 0.0
    success: bool = True
    observations: dict[str, Any] = field(default_factory=dict)
    commands: dict[str, Any] = field(default_factory=dict)
    metrics_delta: dict[str, float] = field(default_factory=dict)
    events: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
