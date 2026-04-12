from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class JointTrajectory:
    """Joint trajectory samples generated with quintic boundary conditions."""

    time_s: tuple[float, ...]
    joints_positions: tuple[tuple[float, ...], ...]
    joints_velocities: tuple[tuple[float, ...], ...]
    joints_accelerations: tuple[tuple[float, ...], ...]

    @property
    def steps(self) -> int:
        return len(self.time_s)

    @property
    def joints_count(self) -> int:
        return 0 if self.steps == 0 else len(self.joints_positions[0])


class QuinticJointTrajectory:
    """Equivalent to legacy QuinticJointTraj for joint-space references."""

    def generate(
        self,
        q0: Sequence[float],
        qf: Sequence[float],
        tf: float,
        dt: float,
    ) -> JointTrajectory:
        if tf <= 0.0:
            raise ValueError("`tf` must be greater than zero.")
        if dt <= 0.0:
            raise ValueError("`dt` must be greater than zero.")

        time_samples_s = self._build_time_samples(tf=tf, dt=dt)
        return self.generate_from_time_samples(
            q0=q0,
            qf=qf,
            time_samples_s=time_samples_s,
        )

    def generate_from_time_samples(
        self,
        q0: Sequence[float],
        qf: Sequence[float],
        time_samples_s: Sequence[float],
    ) -> JointTrajectory:
        q0_values = self._as_vector(q0, "q0")
        qf_values = self._as_vector(qf, "qf")
        t_values = self._as_vector(time_samples_s, "time_samples_s")

        if len(q0_values) != len(qf_values):
            raise ValueError("`q0` and `qf` must have the same size.")
        if len(t_values) < 2:
            raise ValueError("`time_samples_s` must contain at least two samples.")

        t0 = min(t_values)
        tf = max(t_values)
        duration = tf - t0
        if duration <= 0.0:
            raise ValueError("`time_samples_s` must span a positive duration.")

        q_rows: list[tuple[float, ...]] = []
        q_dot_rows: list[tuple[float, ...]] = []
        q_ddot_rows: list[tuple[float, ...]] = []

        for t in t_values:
            tau = (t - t0) / duration
            tau2 = tau * tau
            tau3 = tau2 * tau
            tau4 = tau3 * tau
            tau5 = tau4 * tau

            q_row: list[float] = []
            q_dot_row: list[float] = []
            q_ddot_row: list[float] = []

            for q0_joint, qf_joint in zip(q0_values, qf_values):
                dq = qf_joint - q0_joint

                q_joint = q0_joint + dq * (10.0 * tau3 - 15.0 * tau4 + 6.0 * tau5)
                q_dot_joint = (dq / duration) * (
                    30.0 * tau2 - 60.0 * tau3 + 30.0 * tau4
                )
                q_ddot_joint = (dq / (duration * duration)) * (
                    60.0 * tau - 180.0 * tau2 + 120.0 * tau3
                )

                q_row.append(float(q_joint))
                q_dot_row.append(float(q_dot_joint))
                q_ddot_row.append(float(q_ddot_joint))

            q_rows.append(tuple(q_row))
            q_dot_rows.append(tuple(q_dot_row))
            q_ddot_rows.append(tuple(q_ddot_row))

        return JointTrajectory(
            time_s=t_values,
            joints_positions=tuple(q_rows),
            joints_velocities=tuple(q_dot_rows),
            joints_accelerations=tuple(q_ddot_rows),
        )

    @staticmethod
    def _as_vector(values: Sequence[float], name: str) -> tuple[float, ...]:
        vector = tuple(float(value) for value in values)
        if len(vector) == 0:
            raise ValueError(f"`{name}` cannot be empty.")
        return vector

    @staticmethod
    def _build_time_samples(tf: float, dt: float) -> tuple[float, ...]:
        samples: list[float] = []
        t = 0.0
        while t < tf:
            samples.append(float(t))
            t += dt
        samples.append(float(tf))
        return tuple(samples)


def generate(
    q0: Sequence[float],
    qf: Sequence[float],
    tf: float,
    dt: float,
) -> JointTrajectory:
    """Convenience function for one-shot quintic trajectory generation."""

    return QuinticJointTrajectory().generate(q0=q0, qf=qf, tf=tf, dt=dt)
