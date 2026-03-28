from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import (
    compute_active_track_count,
    compute_mean_tracking_confidence,
)
from manipulator_framework.core.types import TargetType, TrackedTarget, TrackingStatus


def make_track(track_id: str, confidence: float) -> TrackedTarget:
    return TrackedTarget(
        target_id=track_id,
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        confidence=confidence,
        age_steps=3,
        missed_steps=0,
        timestamp=0.0,
    )


def test_compute_mean_tracking_confidence_returns_expected_value() -> None:
    tracks = [
        make_track("t1", 0.8),
        make_track("t2", 0.6),
        make_track("t3", 1.0),
    ]

    metric = compute_mean_tracking_confidence(tracks)

    assert metric.name == "mean_tracking_confidence"
    assert np.isclose(metric.value, 0.8)


def test_compute_active_track_count_returns_track_count() -> None:
    tracks = [
        make_track("t1", 0.8),
        make_track("t2", 0.6),
    ]

    metric = compute_active_track_count(tracks)

    assert metric.name == "active_track_count"
    assert metric.unit == "count"
    assert metric.value == 2.0
