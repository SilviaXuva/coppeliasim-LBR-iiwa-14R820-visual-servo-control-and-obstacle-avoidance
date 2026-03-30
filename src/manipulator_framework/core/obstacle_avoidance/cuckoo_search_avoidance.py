from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from manipulator_framework.core.types import ObstacleState, RobotState, Trajectory
from .avoidance_costs import compute_clearance_cost
from .obstacle_models import AvoidanceResult
from .reference_adapter import TrajectoryReferenceAdapter
from ..contracts.obstacle_interfaces import ObstacleAvoidanceInterface


@dataclass
class CuckooSearchAvoidance(ObstacleAvoidanceInterface):
    """
    Pure avoidance module skeleton.

    Placeholder policy:
        This implements a deterministic candidate search scaffold compatible
        with later replacement by a true cuckoo-search strategy.
    """
    safe_distance: float = 0.6
    candidate_scale: float = 0.05
    _adapter: TrajectoryReferenceAdapter = field(default_factory=TrajectoryReferenceAdapter, init=False, repr=False)

    def adapt_trajectory(
        self,
        reference: Trajectory,
        obstacles: list[ObstacleState],
        robot_state: RobotState,
    ) -> Trajectory:
        avoidance_result = self.adapt_reference(
            reference=reference,
            obstacles=obstacles,
            robot_state=robot_state,
        )
        return self._adapter.adapt(reference, avoidance_result)

    def adapt_reference(
        self,
        reference: Trajectory,
        obstacles: list[ObstacleState],
        robot_state: RobotState,
    ) -> AvoidanceResult:
        if robot_state.end_effector_pose is None:
            raise ValueError("robot_state.end_effector_pose is required for avoidance evaluation.")

        dof = robot_state.joint_state.dof
        zero_delta = np.zeros(dof, dtype=float)
        plus_delta = self.candidate_scale * np.ones(dof, dtype=float)
        minus_delta = -self.candidate_scale * np.ones(dof, dtype=float)

        candidates = [zero_delta, plus_delta, minus_delta]

        best_delta = zero_delta
        best_cost = float("inf")

        for delta in candidates:
            # Explicit placeholder:
            # evaluate only current end-effector pose against current obstacles.
            # A fuller version can propagate candidate joint changes through kinematics.
            cost = compute_clearance_cost(
                end_effector_pose=robot_state.end_effector_pose,
                obstacles=obstacles,
                safe_distance=self.safe_distance,
            )
            cost += 0.1 * float(np.linalg.norm(delta))

            if cost < best_cost:
                best_cost = cost
                best_delta = delta

        return AvoidanceResult(
            best_delta_q=best_delta,
            best_cost=best_cost,
            is_safe=(best_cost <= 1e-9),
        )
