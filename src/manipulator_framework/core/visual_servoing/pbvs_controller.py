from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.types import Pose3D, RobotState, Trajectory
from .reference_generation import PBVSReferenceGenerator
from .visual_error import VisualError, compute_pose_error


@dataclass
class PBVSController:
    """
    Pure PBVS controller.

    It computes visual error from estimated target pose and desired target pose,
    then generates a synthetic trajectory reference.
    """
    reference_generator: PBVSReferenceGenerator

    def compute_reference(
        self,
        robot_state: RobotState,
        current_target_pose: Pose3D,
        desired_target_pose: Pose3D,
        dt: float,
    ) -> tuple[VisualError, Trajectory]:
        if robot_state.joint_state is None:
            raise ValueError("robot_state must contain a joint_state.")

        visual_error = compute_pose_error(current_target_pose, desired_target_pose)
        trajectory = self.reference_generator.generate(
            current_joint_state=robot_state.joint_state,
            visual_error=visual_error,
            dt=dt,
        )
        return visual_error, trajectory
