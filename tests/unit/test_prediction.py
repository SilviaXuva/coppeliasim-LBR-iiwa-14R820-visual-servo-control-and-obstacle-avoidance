from __future__ import annotations

from manipulator_framework.core.tracking import ConstantPositionPredictor, TrackState
from manipulator_framework.core.types import TargetType, TrackingStatus


def test_constant_position_predictor_updates_timestamp() -> None:
    track = TrackState(
        track_id="track_0000",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        timestamp=0.0,
    )

    predictor = ConstantPositionPredictor()
    predicted = predictor.predict(track, timestamp=1.0)

    assert predicted.timestamp == 1.0
