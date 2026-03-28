from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RunSchema:
    """
    Minimal logical schema for one experiment run.
    """
    run_id: str
    experiment_name: str
    scenario_name: str
    backend_name: str
    seed: int
    resolved_config: dict[str, Any]
    tags: tuple[str, ...] = ()
    notes: str = ""
