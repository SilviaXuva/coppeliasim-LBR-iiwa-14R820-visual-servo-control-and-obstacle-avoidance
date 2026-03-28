from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from manipulator_framework.core.perception.observation_models import SemanticObservation
from manipulator_framework.core.perception.association import is_person_observation, is_marker_observation
from manipulator_framework.core.perception.target_semantics import ObservationType
from manipulator_framework.core.types import Pose3D, TargetType, TrackedTarget, TrackingStatus, Twist
from .estimate_models import TargetStateEstimate
from .filters import ExponentialMovingAverageFilter


@dataclass
class SemanticTargetStateEstimator:
    """
    Convert semantic observations into internal target state.

    Placeholder policy:
        Person observations may not have 3D pose yet. In that case, the estimator
        can produce a target without pose and preserve semantic continuity.
    """
    position_filter: ExponentialMovingAverageFilter = field(
        default_factory=lambda: ExponentialMovingAverageFilter(alpha=0.5)
    )

    def estimate(self, observation: SemanticObservation) -> TargetStateEstimate:
        estimated_pose: Pose3D | None = None

        if observation.pose_hint is not None:
            filtered_position = self.position_filter.update(observation.pose_hint.position)
            estimated_pose = Pose3D(
                position=filtered_position,
                orientation_quat_xyzw=observation.pose_hint.orientation_quat_xyzw,
                frame_id=observation.pose_hint.frame_id,
                child_frame_id=observation.pose_hint.child_frame_id,
                timestamp=observation.timestamp,
            )

        if is_person_observation(observation):
            target_type = TargetType.PERSON
        elif is_marker_observation(observation):
            target_type = TargetType.MARKER
        else:
            target_type = TargetType.OBJECT

        target = TrackedTarget(
            target_id=observation.observation_id,
            target_type=target_type,
            status=TrackingStatus.TENTATIVE,
            latest_detection=observation.detection_2d,
            estimated_pose=estimated_pose,
            estimated_twist=None,
            confidence=observation.confidence,
            age_steps=1,
            missed_steps=0,
            timestamp=observation.timestamp,
        )

        return TargetStateEstimate(
            target=target,
            confidence=observation.confidence,
            method="semantic_target_state_estimator",
            timestamp=observation.timestamp,
        )
