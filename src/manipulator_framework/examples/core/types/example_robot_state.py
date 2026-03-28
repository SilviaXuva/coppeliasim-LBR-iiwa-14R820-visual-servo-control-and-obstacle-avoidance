from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import JointState, Pose3D, RobotState, Twist


def main() -> None:
    joint_state = JointState(
        positions=np.array([0.0, 0.1, -0.2, 0.3, 0.0, -0.1, 0.2]),
        velocities=np.zeros(7),
        efforts=np.zeros(7),
        joint_names=(
            "joint_1",
            "joint_2",
            "joint_3",
            "joint_4",
            "joint_5",
            "joint_6",
            "joint_7",
        ),
        timestamp=1.25,
    )

    ee_pose = Pose3D(
        position=np.array([0.45, 0.10, 0.72]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world",
        child_frame_id="tool0",
        timestamp=1.25,
    )

    ee_twist = Twist(
        linear=np.array([0.0, 0.0, 0.0]),
        angular=np.array([0.0, 0.0, 0.0]),
        frame_id="tool0",
        timestamp=1.25,
    )

    robot_state = RobotState(
        joint_state=joint_state,
        end_effector_pose=ee_pose,
        end_effector_twist=ee_twist,
        is_ready=True,
        timestamp=1.25,
    )

    print("DOF:", robot_state.joint_state.dof)
    print(robot_state.to_dict())


if __name__ == "__main__":
    main()
