from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScalarMetric:
    name: str
    value: float
    unit: str = ""
    description: str = ""


@dataclass(frozen=True)
class TimeSeriesSample:
    t: float
    values: dict[str, float]


@dataclass(frozen=True)
class MetricsSnapshot:
    scalar_metrics: tuple[ScalarMetric, ...] = ()
    series: dict[str, tuple[TimeSeriesSample, ...]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
