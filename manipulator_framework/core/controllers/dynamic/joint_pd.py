from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Real

import numpy as np

from ...ports.dynamics_port import DynamicsPort


@dataclass(slots=True, frozen=True)
class JointPDResult:
    joints_accelerations: tuple[float, ...]
    joints_velocities: tuple[float, ...]
    joints_torques: tuple[float, ...]


class JointPDController:
    """
    Joint-space dynamic PD controller with velocity output.

    Controller equation:
    - tau = Kp*(joints_positions_ref - q) + Kv*(joints_velocities_ref - dq) + g(q)
    - tau is saturated by injected torque limits
    - ddq = M(q)^(-1) * (tau - C(q, dq)*dq - g(q))
    - dq = dq + ddq * dt
    """

    def __init__(
        self,
        dynamics: DynamicsPort,
        kp: Real | Sequence[float] | Sequence[Sequence[float]] | np.ndarray,
        kv: Real | Sequence[float] | Sequence[Sequence[float]] | np.ndarray,
        joints_count: int,
        joints_torques_min: Sequence[float],
        joints_torques_max: Sequence[float],
    ) -> None:
        if joints_count <= 0:
            raise ValueError("`joints_count` must be greater than zero.")

        self._dynamics = dynamics
        self._joints_count = joints_count
        self._kp = self._normalize_gain(kp, joints_count, "kp")
        self._kv = self._normalize_gain(kv, joints_count, "kv")
        self._joints_torques_min = np.asarray(
            self._as_vector(joints_torques_min, joints_count, "joints_torques_min"), dtype=float
        )
        self._joints_torques_max = np.asarray(
            self._as_vector(joints_torques_max, joints_count, "joints_torques_max"), dtype=float
        )

        if np.any(self._joints_torques_min > self._joints_torques_max):
            raise ValueError("Each `joints_torques_min` value must be lower than `joints_torques_max`.")

    @property
    def dt(self) -> float:
        return self._dt

    def compute(
        self,
        joints_positions: Sequence[float],
        joints_positions_ref: Sequence[float],
        joints_velocities: Sequence[float],
        joints_velocities_ref: Sequence[float],
        dt: float = 0.0,
    ) -> JointPDResult:
        if dt < 0.0:
            raise ValueError("`dt` must be greater than zero.")

        q = np.asarray(
            self._as_vector(joints_positions, self._joints_count, "joints_positions"), dtype=float
        )
        q_ref = np.asarray(
            self._as_vector(joints_positions_ref, self._joints_count, "joints_positions_ref"), dtype=float
        )
        dq = np.asarray(
            self._as_vector(joints_velocities, self._joints_count, "joints_velocities"), dtype=float
        )
        dq_ref = np.asarray(
            self._as_vector(joints_velocities_ref, self._joints_count, "joints_velocities_ref"), dtype=float
        )

        q_err = q_ref - q
        dq_err = dq_ref - dq

        inertia_matrix = self._as_matrix(
            self._dynamics.inertia(q),
            self._joints_count,
            "inertia(joints_positions)",
        )
        coriolis_matrix = self._as_matrix(
            self._dynamics.coriolis(q, dq),
            self._joints_count,
            "coriolis(joints_positions, joints_velocities)",
        )
        gravity_vector = np.asarray(
            self._as_vector(
                self._dynamics.gravity(q),
                self._joints_count,
                "gravity(joints_positions)",
            ),
            dtype=float,
        )

        b = coriolis_matrix @ dq
        tau_ctrl = self._kp @ q_err + self._kv @ dq_err + gravity_vector
        tau_sat = np.clip(tau_ctrl, a_min=self._joints_torques_min, a_max=self._joints_torques_max)
        rhs = tau_sat - b - gravity_vector

        ddq_ctrl = self._solve_acceleration(inertia_matrix, rhs)
        dq_ctrl = dq + ddq_ctrl * dt

        return JointPDResult(
            joints_accelerations=tuple(float(value) for value in ddq_ctrl),
            joints_velocities=tuple(float(value) for value in dq_ctrl),
            joints_torques=tuple(float(value) for value in tau_sat),
        )

    def update(
        self,
        joints_positions: Sequence[float],
        joints_positions_ref: Sequence[float],
        joints_velocities: Sequence[float],
        joints_velocities_ref: Sequence[float],
        dt: float = 0.0,
    ) -> JointPDResult:
        return self.compute(
            joints_positions=joints_positions,
            joints_positions_ref=joints_positions_ref,
            joints_velocities=joints_velocities,
            joints_velocities_ref=joints_velocities_ref,
            dt=dt,
        )

    @staticmethod
    def _normalize_gain(
        gain: Real | Sequence[float] | Sequence[Sequence[float]] | np.ndarray,
        joints_count: int,
        gain_name: str,
    ) -> np.ndarray:
        if isinstance(gain, Real):
            return np.eye(joints_count, dtype=float) * float(gain)

        if isinstance(gain, (str, bytes)):
            raise ValueError(f"`{gain_name}` must contain numeric values.") from None

        try:
            gain_array = np.asarray(gain, dtype=float)
        except (TypeError, ValueError):
            raise ValueError(f"`{gain_name}` must contain numeric values.") from None

        if gain_array.ndim == 0:
            return np.eye(joints_count, dtype=float) * float(gain_array.item())
        if gain_array.ndim == 1:
            if gain_array.shape[0] != joints_count:
                raise ValueError(
                    f"`{gain_name}` vector must have {joints_count} elements."
                )
            return np.diag(gain_array)
        if gain_array.ndim == 2:
            if gain_array.shape != (joints_count, joints_count):
                raise ValueError(
                    f"`{gain_name}` matrix must be {joints_count}x{joints_count}."
                )
            return gain_array

        raise ValueError(f"`{gain_name}` must be scalar, vector or square matrix.")

    @staticmethod
    def _as_vector(
        values: Sequence[float],
        size: int,
        values_name: str,
    ) -> tuple[float, ...]:
        try:
            vector = tuple(float(value) for value in values)
        except (TypeError, ValueError):
            raise ValueError(
                f"`{values_name}` must contain numeric values."
            ) from None
        if len(vector) != size:
            raise ValueError(f"`{values_name}` must be a vector with {size} elements.")
        return vector

    @staticmethod
    def _as_matrix(values: object, size: int, values_name: str) -> np.ndarray:
        try:
            matrix = np.asarray(values, dtype=float)
        except (TypeError, ValueError):
            raise ValueError(f"`{values_name}` must contain numeric values.") from None
        if matrix.shape != (size, size):
            raise ValueError(f"`{values_name}` must be a {size}x{size} matrix.")
        return matrix

    @staticmethod
    def _solve_acceleration(inertia_matrix: np.ndarray, rhs: np.ndarray) -> np.ndarray:
        """
        Solve M*ddq = rhs with robustness against singular/ill-conditioned inertia.
        """
        try:
            condition_number = float(np.linalg.cond(inertia_matrix))
        except np.linalg.LinAlgError:
            condition_number = float("inf")

        if not np.isfinite(condition_number) or condition_number > 1e12:
            return np.linalg.pinv(inertia_matrix) @ rhs

        try:
            return np.linalg.solve(inertia_matrix, rhs)
        except np.linalg.LinAlgError:
            return np.linalg.pinv(inertia_matrix) @ rhs
