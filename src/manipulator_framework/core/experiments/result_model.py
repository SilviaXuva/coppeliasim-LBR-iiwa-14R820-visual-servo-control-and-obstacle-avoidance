from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.core.types.execution import CycleResult
from manipulator_framework.core.types.metrics import MetricsSnapshot
from .artifact_model import RunArtifact


@dataclass(frozen=True)
class RunResult:
    """
    Canonical result model for one full run.
    Contains only run-level data and the canonical cycle stream.
    """
    run_id: str
    success: bool
    num_cycles: int
    summary: dict[str, Any]
    metrics: MetricsSnapshot
    artifacts: tuple[RunArtifact, ...] = ()
    resolved_config: dict[str, Any] = field(default_factory=dict)
    seed: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    cycle_results: tuple[CycleResult, ...] = ()

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    def scalar_metrics_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for metric in self.metrics.scalar_metrics:
            rows.append(
                {
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "description": metric.description,
                }
            )
        return rows

    def series_samples_dict(self) -> dict[str, list[dict[str, Any]]]:
        payload: dict[str, list[dict[str, Any]]] = {}
        for series_name, samples in self.metrics.series.items():
            payload[series_name] = [
                {
                    "t": sample.t,
                    "values": dict(sample.values),
                }
                for sample in samples
            ]
        return payload

    def artifacts_manifest(self) -> list[dict[str, str]]:
        return [
            {
                "name": artifact.name,
                "path": artifact.path,
                "kind": artifact.kind,
                "description": artifact.description,
            }
            for artifact in self.artifacts
        ]

    def summary_dict(self) -> dict[str, Any]:
        payload = dict(self.summary)
        payload.update(
            {
                "run_id": self.run_id,
                "success": self.success,
                "num_cycles": self.num_cycles,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration": self.duration,
                "artifacts": self.artifacts_manifest(),
            }
        )
        return payload

    def metadata_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "success": self.success,
            "num_cycles": self.num_cycles,
            "seed": self.seed,
            "resolved_config": self.resolved_config,
            "summary": dict(self.summary),
        }

    def metrics_dict(self) -> dict[str, Any]:
        return {
            "scalar_metrics": self.scalar_metrics_rows(),
            "series": self.series_samples_dict(),
            "metadata": dict(self.metrics.metadata),
        }
