from __future__ import annotations

import numpy as np

from manipulator_framework.core.obstacle_avoidance import CuckooSearchAvoidance
from manipulator_framework.core.types import JointState, ObstacleState, Pose3D, RobotState, Trajectory, TrajectorySample


def test_cuckoo_search_avoidance_returns_result() -> None:
    robot_state = RobotState(
        joint_state=JointState(
            positions=np.zeros(7),
            velocities=np.zeros(7),
            joint_names=tuple(f"joint_{i+1}" for i in range(7)),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.5, 0.0, 0.7]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        ),
        timestamp=0.0,
    )

    reference = Trajectory(
        samples=(
            TrajectorySample(time_from_start=0.0, joint_state=robot_state.joint_state),
        ),
        name="ref",
        timestamp=0.0,
    )

    obstacle = ObstacleState(
        obstacle_id="obs_001",
        pose=Pose3D(
            position=np.array([0.52, 0.0, 0.7]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        ),
        radius=0.1,
        confidence=1.0,
        timestamp=0.0,
    )

    avoidance = CuckooSearchAvoidance()
    result = avoidance.adapt_reference(reference, [obstacle], robot_state)

    assert result.best_delta_q.shape == (7,)
