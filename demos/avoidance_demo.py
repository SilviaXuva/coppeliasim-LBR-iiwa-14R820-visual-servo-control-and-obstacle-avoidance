"""
Obstacle Avoidance Demo.

This demo demonstrates how the CuckooSearchAvoidance module evaluates 
end-effector pose against observed obstacles and computes candidate corrections.
"""

from __future__ import annotations

import numpy as np

from manipulator_framework.core.obstacle_avoidance.cuckoo_search_avoidance import CuckooSearchAvoidance
from manipulator_framework.core.types import Pose3D, ObstacleState, RobotState, JointState
from manipulator_framework.core.types.enums import ObstacleType

def main():
    print("--- Avoidance Demo ---")
    
    # Initialize the avoidance module
    # safe_distance = 0.5 (meters)
    avoidance = CuckooSearchAvoidance(safe_distance=0.5, candidate_scale=0.01)

    # Current robot state at (0, 0, 0)
    current_state = RobotState(
        joint_state=JointState(
            positions=np.zeros(7),
            velocities=np.zeros(7),
            joint_names=tuple(f"joint_{i}" for i in range(7)),
            timestamp=0.0
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.0, 0.0, 0.0]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            timestamp=0.0
        ),
        timestamp=0.0
    )

    # Obstacle at (0.3, 0.0, 0.0) - inside safe distance
    obs1 = ObstacleState(
        obstacle_id="sphere_01",
        obstacle_type=ObstacleType.SPHERE,
        pose=Pose3D(
            position=np.array([0.3, 0.0, 0.0]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            timestamp=0.0
        ),
        size_params={"radius": 0.1},
        velocity=np.zeros(3),
        confidence=1.0,
        timestamp=0.0
    )

    print(f"\nRobot at: {current_state.end_effector_pose.position}")
    print(f"Obstacle at: {obs1.pose.position}")
    print(f"Safe distance threshold: {avoidance.safe_distance}")

    # Process avoidance
    result = avoidance.adapt_reference(
        reference=None, # Skeleton currently ignores the reference
        obstacles=[obs1],
        robot_state=current_state
    )

    print("-" * 20)
    print(f"Avoidance Result:")
    print(f"  Is Safe: {result.is_safe}")
    print(f"  Best Cost: {result.best_cost}")
    print(f"  Best Correction (delta_q): {result.best_delta_q}")
    print("-" * 20)
    print("Demo finished.")

if __name__ == "__main__":
    main()
