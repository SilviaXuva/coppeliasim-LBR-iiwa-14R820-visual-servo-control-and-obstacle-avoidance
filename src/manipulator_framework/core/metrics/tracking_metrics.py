from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics.metric_models import ScalarMetric
from manipulator_framework.core.types import TrackedTarget


def compute_mean_tracking_confidence(tracks: list[TrackedTarget]) -> ScalarMetric:
    if not tracks:
        return ScalarMetric(
            name="mean_tracking_confidence",
            value=0.0,
            unit="",
            description="Mean confidence of tracked targets.",
        )

    values = [float(track.confidence) for track in tracks]
    return ScalarMetric(
        name="mean_tracking_confidence",
        value=float(np.mean(values)),
        unit="",
        description="Mean confidence of tracked targets.",
    )


def compute_active_track_count(tracks: list[TrackedTarget]) -> ScalarMetric:
    return ScalarMetric(
        name="active_track_count",
        value=float(len(tracks)),
        unit="count",
        description="Number of active tracks in current run or snapshot.",
    )
