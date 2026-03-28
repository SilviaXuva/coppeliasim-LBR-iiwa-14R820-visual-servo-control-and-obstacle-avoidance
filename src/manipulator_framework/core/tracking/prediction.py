from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.tracking.track_state import TrackState
from manipulator_framework.core.types import Pose3D


@dataclass
class ConstantPositionPredictor:
    """
    Minimal predictor.

    Placeholder:
        Keeps pose constant if no velocity model is available.
    """

    def predict(self, track: TrackState, timestamp: float) -> TrackState:
        track.timestamp = timestamp
        return track
