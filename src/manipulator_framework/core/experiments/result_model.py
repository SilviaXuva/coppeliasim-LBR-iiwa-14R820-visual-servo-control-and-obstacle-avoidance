from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.core.metrics.metric_models import MetricsSnapshot
from .artifact_model import RunArtifact
from .run_schema import RunSchema


@dataclass(frozen=True)
class RunResult:
    """
    Canonical result model for one persisted experiment/application run.
    """

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

    @property
    def run_id(self) -> str:
        return self.run_schema.run_id

    @property
    def experiment_name(self) -> str:
        return self.run_schema.experiment_name

    @property
    def scenario_name(self) -> str:
        return self.run_schema.scenario_name

    @property
    def backend_name(self) -> str:
        return self.run_schema.backend_name

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
        return {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "scenario_name": self.scenario_name,
            "backend_name": self.backend_name,
            "success": self.success,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration": self.duration,
            "artifacts": self.artifacts_manifest(),
        }

    def metadata_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "scenario_name": self.scenario_name,
            "backend_name": self.backend_name,
            "seed": self.run_schema.seed,
            "tags": list(self.run_schema.tags),
            "notes": self.run_schema.notes,
            "metadata": dict(self.metadata),
        }

    def metrics_dict(self) -> dict[str, Any]:
        return {
            "scalar_metrics": self.scalar_metrics_rows(),
            "series": self.series_samples_dict(),
            "metadata": dict(self.metrics.metadata),
        }
