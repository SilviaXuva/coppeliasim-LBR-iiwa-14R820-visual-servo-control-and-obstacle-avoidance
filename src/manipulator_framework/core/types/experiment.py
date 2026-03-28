from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .aliases import Timestamp
from .mixins import SerializableMixin


@dataclass(frozen=True)
class ExperimentResult(SerializableMixin):
    experiment_name: str
    run_id: str
    success: bool
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: Timestamp = 0.0
    finished_at: Timestamp = 0.0

    @property
    def duration(self) -> float:
        return self.finished_at - self.started_at
