from __future__ import annotations

from dataclasses import dataclass, field

from manipulator_framework.core.types import (
    CameraFrame,
    ControlOutput,
    MarkerDetection,
    ObstacleState,
    PersonDetection,
    Pose3D,
    RobotState,
    Trajectory,
    TrackedTarget,
)


@dataclass
class RuntimeContext:
    """
    Mutable execution context shared across one pipeline cycle.
    """
    cycle_index: int = 0
    timestamp: float = 0.0

    robot_state: RobotState | None = None
    camera_frame: CameraFrame | None = None

    marker_detections: list[MarkerDetection] = field(default_factory=list)
    person_detections: list[PersonDetection] = field(default_factory=list)
    tracked_targets: list[TrackedTarget] = field(default_factory=list)
    obstacles: list[ObstacleState] = field(default_factory=list)

    target_pose: Pose3D | None = None
    trajectory_reference: Trajectory | None = None
    control_output: ControlOutput | None = None

    metadata: dict[str, object] = field(default_factory=dict)
