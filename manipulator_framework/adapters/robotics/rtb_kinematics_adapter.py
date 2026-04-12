from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from roboticstoolbox import DHRobot, ERobot
from roboticstoolbox.tools.trajectory import ctraj, jtraj
from spatialmath import SE3

from ...core.models.pose import Pose
from ...core.ports.kinematics_port import JacobianMatrix, KinematicsPort


class RTBKinematicsAdapter(KinematicsPort):
    """Implements KinematicsPort using Robotics Toolbox."""

    def __init__(self, robot: DHRobot | ERobot) -> None:
        self._robot = robot

    def forward_kinematics(self, joints_positions: Sequence[float]) -> Pose:
        transform = self._robot.fkine(np.asarray(joints_positions, dtype=float))
        return self._se3_to_pose(transform)

    def inverse_kinematics(
        self,
        target_pose: Pose,
        seed_joints_positions: Sequence[float] | None = None,
    ) -> tuple[float, ...]:
        target_transform = self._pose_to_se3(target_pose)
        q0 = None
        if seed_joints_positions is not None:
            q0 = np.asarray(seed_joints_positions, dtype=float)
        solution = self._robot.ikine_LMS(target_transform, q0=q0)
        if hasattr(solution, "success") and not solution.success:
            raise RuntimeError("Inverse kinematics did not converge.")
        return tuple(float(value) for value in solution.q)

    def jacobian(self, joints_positions: Sequence[float]) -> JacobianMatrix:
        jacobian = self._robot.jacob0_analytical(
            np.asarray(joints_positions, dtype=float), "rpy/zyx"
        )
        jacobian_rows = np.asarray(jacobian, dtype=float).tolist()
        return tuple(tuple(float(value) for value in row) for row in jacobian_rows)

    def plan_joint_trajectory(
        self,
        start_joints_positions: Sequence[float],
        goal_joints_positions: Sequence[float],
        time_samples_s: Sequence[float],
    ) -> Sequence[tuple[float, ...]]:
        trajectory = jtraj(
            np.asarray(start_joints_positions, dtype=float),
            np.asarray(goal_joints_positions, dtype=float),
            np.asarray(time_samples_s, dtype=float),
        )
        return tuple(
            tuple(float(value) for value in joints_sample)
            for joints_sample in np.asarray(trajectory.q, dtype=float).tolist()
        )

    def plan_cartesian_trajectory(
        self,
        start_pose: Pose,
        goal_pose: Pose,
        time_samples_s: Sequence[float],
    ) -> Sequence[Pose]:
        trajectory = ctraj(
            self._pose_to_se3(start_pose),
            self._pose_to_se3(goal_pose),
            np.asarray(time_samples_s, dtype=float),
        )
        return tuple(
            self._se3_to_pose(SE3(transform_matrix))
            for transform_matrix in trajectory.A
            if transform_matrix is not None
        )

    @staticmethod
    def _pose_to_se3(pose: Pose) -> SE3:
        return SE3.Trans(pose.x, pose.y, pose.z) * SE3.RPY(
            [pose.roll, pose.pitch, pose.yaw],
            order="zyx",
        )

    @staticmethod
    def _se3_to_pose(transform: SE3) -> Pose:
        rpy = transform.rpy()
        return Pose(
            x=float(transform.t[0]),
            y=float(transform.t[1]),
            z=float(transform.t[2]),
            roll=float(rpy[0]),
            pitch=float(rpy[1]),
            yaw=float(rpy[2]),
        )
