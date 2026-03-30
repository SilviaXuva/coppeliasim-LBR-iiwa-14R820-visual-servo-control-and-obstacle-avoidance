from __future__ import annotations

import numpy as np

from manipulator_framework.core.types.metrics import ScalarMetric


def compute_mean_cycle_latency(latencies: list[float]) -> ScalarMetric:
    if not latencies:
        raise ValueError("latencies cannot be empty.")

    return ScalarMetric(
        name="mean_cycle_latency",
        value=float(np.mean(np.asarray(latencies, dtype=float))),
        unit="s",
        description="Mean runtime cycle latency.",
    )


def compute_success_rate(success_flags: list[bool]) -> ScalarMetric:
    if not success_flags:
        raise ValueError("success_flags cannot be empty.")

    values = np.asarray(success_flags, dtype=float)
    return ScalarMetric(
        name="success_rate",
        value=float(np.mean(values)),
        unit="ratio",
        description="Fraction of successful cycles or runs.",
    )
