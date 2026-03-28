from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import Pose3D
from manipulator_framework.core.perception.observation_models import SemanticObservation
from manipulator_framework.core.perception.association import is_marker_observation
from .estimate_models import PoseEstimate


@dataclass
class MarkerPoseEstimator:
    """
    Pure core estimator for marker pose.

    Placeholder policy:
        This class assumes the adapter already extracted a pose hint when available.
        The core only validates and wraps the semantic result.
    """

    output_frame_id: str = "camera"
    output_child_frame_prefix: str = "marker"

    def estimate(self, observation: SemanticObservation) -> PoseEstimate | None:
        if not is_marker_observation(observation):
            return None

        if observation.pose_hint is None or observation.marker_detection is None:
            return None

        marker_id = observation.marker_detection.marker_id
        pose = Pose3D(
            position=np.asarray(observation.pose_hint.position, dtype=float),
            orientation_quat_xyzw=np.asarray(observation.pose_hint.orientation_quat_xyzw, dtype=float),
            frame_id=observation.pose_hint.frame_id,
            child_frame_id=f"{self.output_child_frame_prefix}_{marker_id}",
            timestamp=observation.timestamp,
        )

        return PoseEstimate(
            pose=pose,
            confidence=observation.confidence,
            method="marker_pose_hint",
            timestamp=observation.timestamp,
        )
