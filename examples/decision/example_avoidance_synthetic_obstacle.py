from __future__ import annotations

import numpy as np

from manipulator_framework.core.obstacle_avoidance import CuckooSearchAvoidance
from manipulator_framework.core.types import JointState, ObstacleState, Pose3D, RobotState, Trajectory, TrajectorySample


def main() -> None:
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
            frame_id="world",
            child_frame_id="tool0",
            timestamp=0.0,
        ),
        timestamp=0.0,
    )

    reference = Trajectory(
        samples=(
            TrajectorySample(time_from_start=0.0, joint_state=robot_state.joint_state),
            TrajectorySample(
                time_from_start=0.1,
                joint_state=JointState(
                    positions=0.1 * np.ones(7),
                    velocities=np.zeros(7),
                    accelerations=np.zeros(7),
                    joint_names=robot_state.joint_state.joint_names,
                    timestamp=0.1,
                ),
            ),
        ),
        name="synthetic_reference",
        timestamp=0.0,
    )

    obstacle = ObstacleState(
        obstacle_id="person_001",
        pose=Pose3D(
            position=np.array([0.55, 0.0, 0.7]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="person_001",
            timestamp=0.0,
        ),
        radius=0.25,
        source="synthetic",
        confidence=1.0,
        timestamp=0.0,
    )

    avoidance = CuckooSearchAvoidance(safe_distance=0.5, candidate_scale=0.02)
    result = avoidance.adapt_reference(reference, [obstacle], robot_state)

    print("Best delta q:", result.best_delta_q)
    print("Best cost:", result.best_cost)
    print("Is safe:", result.is_safe)


if __name__ == "__main__":
    main()
