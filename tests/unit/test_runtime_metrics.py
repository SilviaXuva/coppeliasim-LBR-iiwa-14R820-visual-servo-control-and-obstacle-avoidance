from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import (
    compute_mean_cycle_latency,
    compute_success_rate,
)


def test_compute_mean_cycle_latency_returns_average_latency() -> None:
    metric = compute_mean_cycle_latency([0.01, 0.03, 0.02])

    assert metric.name == "mean_cycle_latency"
    assert metric.unit == "s"
    assert np.isclose(metric.value, 0.02)


def test_compute_success_rate_returns_fraction_of_successes() -> None:
    metric = compute_success_rate([True, False, True, True])

    assert metric.name == "success_rate"
    assert metric.unit == "ratio"
    assert np.isclose(metric.value, 0.75)
