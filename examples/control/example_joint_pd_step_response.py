from __future__ import annotations

import numpy as np

from manipulator_framework.core.control import JointSpacePDController
from manipulator_framework.core.types import JointState, RobotState, TrajectorySample


def make_robot_state(q: np.ndarray, dq: np.ndarray, t: float) -> RobotState:
    return RobotState(
        joint_state=JointState(
            positions=q,
            velocities=dq,
            joint_names=tuple(f"joint_{i+1}" for i in range(len(q))),
            timestamp=t,
        ),
        timestamp=t,
    )


def make_reference(q_ref: np.ndarray, dq_ref: np.ndarray, t: float) -> TrajectorySample:
    return TrajectorySample(
        time_from_start=t,
        joint_state=JointState(
            positions=q_ref,
            velocities=dq_ref,
            accelerations=np.zeros_like(q_ref),
            joint_names=tuple(f"joint_{i+1}" for i in range(len(q_ref))),
            timestamp=t,
        ),
    )


def main() -> None:
    controller = JointSpacePDController(
        dof=7,
        kp=10.0 * np.ones(7),
        kd=2.0 * np.ones(7),
        output_limit=20.0 * np.ones(7),
    )

    q = np.zeros(7)
    dq = np.zeros(7)
    q_ref = np.array([0.1, 0.0, -0.1, 0.2, 0.0, 0.1, -0.05], dtype=float)
    dt = 0.01

    for step in range(5):
        t = step * dt
        robot_state = make_robot_state(q, dq, t)
        reference = make_reference(q_ref, np.zeros(7), t)

        output = controller.compute_control(robot_state, reference, dt)
        tau = output.torque_command.torques

        print(f"step={step}, torque={tau}")
        dq = dq + tau * dt
        q = q + dq * dt


if __name__ == "__main__":
    main()
