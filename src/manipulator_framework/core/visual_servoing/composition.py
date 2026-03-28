from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.obstacle_avoidance.cuckoo_search_avoidance import CuckooSearchAvoidance
from manipulator_framework.core.obstacle_avoidance.reference_adapter import TrajectoryReferenceAdapter
from manipulator_framework.core.types import ObstacleState, Pose3D, RobotState, Trajectory
from .pbvs_controller import PBVSController
from .visual_error import VisualError


@dataclass
class PBVSAvoidanceComposer:
    """
    Minimal composition layer for PBVS + obstacle avoidance.
    """
    pbvs_controller: PBVSController
    avoidance: CuckooSearchAvoidance
    trajectory_adapter: TrajectoryReferenceAdapter

    def compute_reference(
        self,
        robot_state: RobotState,
        current_target_pose: Pose3D,
        desired_target_pose: Pose3D,
        obstacles: list[ObstacleState],
        dt: float,
    ) -> tuple[VisualError, Trajectory]:
        visual_error, pbvs_reference = self.pbvs_controller.compute_reference(
            robot_state=robot_state,
            current_target_pose=current_target_pose,
            desired_target_pose=desired_target_pose,
            dt=dt,
        )

        avoidance_result = self.avoidance.adapt_reference(
            reference=pbvs_reference,
            obstacles=obstacles,
            robot_state=robot_state,
        )

        final_reference = self.trajectory_adapter.adapt(pbvs_reference, avoidance_result)
        return visual_error, final_reference
