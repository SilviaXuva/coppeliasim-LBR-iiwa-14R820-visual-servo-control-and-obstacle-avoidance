from __future__ import annotations

import numpy as np

from manipulator_framework.core.visual_servoing import PBVSController, PBVSReferenceGenerator
from manipulator_framework.core.types import JointState, Pose3D, RobotState


def main() -> None:
    robot_state = RobotState(
        joint_state=JointState(
            positions=np.zeros(7),
            velocities=np.zeros(7),
            joint_names=tuple(f"joint_{i+1}" for i in range(7)),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.4, 0.0, 0.7]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="tool0",
            timestamp=0.0,
        ),
        timestamp=0.0,
    )

    current_target_pose = Pose3D(
        position=np.array([0.6, -0.1, 0.8]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world",
        child_frame_id="target",
        timestamp=0.0,
    )

    desired_target_pose = Pose3D(
        position=np.array([0.5, 0.0, 0.7]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world",
        child_frame_id="target_desired",
        timestamp=0.0,
    )

    controller = PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.8))
    visual_error, trajectory = controller.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_target_pose,
        desired_target_pose=desired_target_pose,
        dt=0.1,
    )

    print("Visual error norm:", visual_error.norm)
    print("Trajectory:", trajectory.to_dict())


if __name__ == "__main__":
    main()
