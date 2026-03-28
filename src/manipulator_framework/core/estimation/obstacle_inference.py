from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.types import ObstacleState, TrackedTarget


@dataclass
class PersonAsObstacleInference:
    """
    Infer obstacle state from a tracked person target.

    Placeholder:
        Radius is a configurable semantic approximation.
    """
    default_radius: float = 0.35
    source_name: str = "person_state_estimator"

    def infer(self, target: TrackedTarget) -> ObstacleState | None:
        if target.estimated_pose is None:
            return None

        return ObstacleState(
            obstacle_id=f"obstacle:{target.target_id}",
            pose=target.estimated_pose,
            velocity=target.estimated_twist,
            radius=self.default_radius,
            source=self.source_name,
            confidence=target.confidence,
            timestamp=target.timestamp,
        )
