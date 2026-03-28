from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.core.metrics.metric_models import MetricsSnapshot
from .artifact_model import RunArtifact
from .run_schema import RunSchema


@dataclass(frozen=True)
class RunResult:
    run_schema: RunSchema
    metrics: MetricsSnapshot
    artifacts: tuple[RunArtifact, ...] = ()
    success: bool = True
    started_at: float = 0.0
    finished_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return self.finished_at - self.started_at
