from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScalarMetric:
    """
    Representation of a single scientific scalar metric.
    """
    name: str
    value: float
    unit: str = ""
    description: str = ""


@dataclass(frozen=True)
class TimeSeriesSample:
    """
    A single point in time for a collected metrics series.
    """
    t: float
    values: dict[str, float]


@dataclass(frozen=True)
class MetricsSnapshot:
    """
    Immutable collection of scalar metrics and series samples at a point in time.
    """
    scalar_metrics: tuple[ScalarMetric, ...] = ()
    series: dict[str, tuple[TimeSeriesSample, ...]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
