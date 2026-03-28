from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import JointState, Trajectory
from .interfaces import JointTrajectoryPlannerInterface
from .quintic_polynomial import QuinticBoundaryConditions, QuinticPolynomial
from .sampling import make_trajectory, make_trajectory_sample
from .time_parameterization import build_time_grid


@dataclass
class QuinticJointTrajectoryPlanner(JointTrajectoryPlannerInterface):
    """
    Pure joint-space planner using one quintic scalar profile per joint.
    """

    trajectory_name: str = "quintic_joint_trajectory"

    def plan(
        self,
        start: JointState,
        goal: JointState,
        duration: float,
        time_step: float,
    ) -> Trajectory:
        if start.dof != goal.dof:
            raise ValueError("start and goal must have the same number of joints.")

        q0 = np.asarray(start.positions, dtype=float)
        qf = np.asarray(goal.positions, dtype=float)

        v0 = np.zeros_like(q0) if start.velocities is None else np.asarray(start.velocities, dtype=float)
        vf = np.zeros_like(qf) if goal.velocities is None else np.asarray(goal.velocities, dtype=float)

        a0 = np.zeros_like(q0) if start.accelerations is None else np.asarray(start.accelerations, dtype=float)
        af = np.zeros_like(qf) if goal.accelerations is None else np.asarray(goal.accelerations, dtype=float)

        profiles = [
            QuinticPolynomial.from_boundary_conditions(
                QuinticBoundaryConditions(
                    q0=q0_i,
                    qf=qf_i,
                    v0=v0_i,
                    vf=vf_i,
                    a0=a0_i,
                    af=af_i,
                ),
                duration=duration,
            )
            for q0_i, qf_i, v0_i, vf_i, a0_i, af_i in zip(q0, qf, v0, vf, a0, af)
        ]

        times = build_time_grid(duration=duration, time_step=time_step)
        samples = []

        for t in times:
            positions = []
            velocities = []
            accelerations = []

            for profile in profiles:
                q, v, a = profile.evaluate(float(t))
                positions.append(q)
                velocities.append(v)
                accelerations.append(a)

            samples.append(
                make_trajectory_sample(
                    positions=np.array(positions, dtype=float),
                    velocities=np.array(velocities, dtype=float),
                    accelerations=np.array(accelerations, dtype=float),
                    time_from_start=float(t),
                    joint_names=start.joint_names,
                )
            )

        return make_trajectory(samples=samples, name=self.trajectory_name, timestamp=start.timestamp)
