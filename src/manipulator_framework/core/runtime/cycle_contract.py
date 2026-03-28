from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StepResult:
    """
    Result of a single pipeline step.
    """
    step_name: str
    success: bool
    message: str = ""
    timestamp: float = 0.0


@dataclass(frozen=True)
class CycleResult:
    """
    Result of one full execution cycle.
    """
    cycle_index: int
    success: bool
    step_results: tuple[StepResult, ...]
    timestamp: float = 0.0
    message: str = ""
