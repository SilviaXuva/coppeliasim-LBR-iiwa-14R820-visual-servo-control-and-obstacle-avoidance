from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Real

import numpy as np


@dataclass(slots=True, frozen=True)
class JointPIResult:
    joints_velocities: tuple[float, ...]
    joints_positions_error: tuple[float, ...]
    next_integral_state: tuple[float, ...]


class JointPIController:
    """
    Joint-space PI controller equivalent to legacy JointSpaceController.

    Legacy behavior preserved:
    - integral state is the previous joint error
    - command = Kp*e + Ki*(int_state + e*dt) + dq_ref
    """

    def __init__(
        self,
        kp: Real | Sequence[float] | Sequence[Sequence[float]] | np.ndarray,
        ki: Real | Sequence[float] | Sequence[Sequence[float]] | np.ndarray,
        joints_count: int,
        initial_integral_state: Sequence[float] | None = None,
    ) -> None:
        if joints_count <= 0:
            raise ValueError("`joints_count` must be greater than zero.")

        self._joints_count = joints_count
        self._kp = self._normalize_gain(kp, joints_count, "kp")
        self._ki = self._normalize_gain(ki, joints_count, "ki")
        self._integral_state = tuple(0.0 for _ in range(joints_count))
        self.reset(initial_integral_state)

    @property
    def integral_state(self) -> tuple[float, ...]:
        return self._integral_state

    def reset(self, integral_state: Sequence[float] | None = None) -> None:
        if integral_state is None:
            self._integral_state = tuple(0.0 for _ in range(self._joints_count))
            return
        self._integral_state = self._as_vector(
            integral_state, self._joints_count, "integral_state"
        )

    def compute(
        self,
        joints_positions: Sequence[float],
        joints_positions_ref: Sequence[float],
        joints_velocities_ref: Sequence[float],
        dt: float = 0.0,
        integral_state: Sequence[float] | None = None,
    ) -> JointPIResult:
        if dt < 0.0:
            raise ValueError("`dt` must be non-negative.")

        q = np.asarray(
            self._as_vector(joints_positions, self._joints_count, "joints_positions"),
            dtype=float,
        )
        q_ref = np.asarray(
            self._as_vector(
                joints_positions_ref, self._joints_count, "joints_positions_ref"
            ),
            dtype=float,
        )
        if joints_velocities_ref is None:
            dq_ref = np.zeros(self._joints_count, dtype=float)
        else:
            dq_ref = np.asarray(
                self._as_vector(
                    joints_velocities_ref,
                    self._joints_count,
                    "joints_velocities_ref",
                ),
                dtype=float,
            )

        if integral_state is None:
            int_state = np.asarray(self._integral_state, dtype=float)
        else:
            int_state = np.asarray(
                self._as_vector(integral_state, self._joints_count, "integral_state"),
                dtype=float,
            )

        q_err = q_ref - q
        dq_ctrl = (
            self._kp @ q_err
            + self._ki @ (int_state + q_err * float(dt))
            + dq_ref
        )

        q_err_tuple = tuple(float(value) for value in q_err)
        dq_ctrl_tuple = tuple(float(value) for value in dq_ctrl)

        return JointPIResult(
            joints_velocities=dq_ctrl_tuple,
            joints_positions_error=q_err_tuple,
            next_integral_state=q_err_tuple,
        )

    def update(
        self,
        joints_positions: Sequence[float],
        joints_positions_ref: Sequence[float],
        joints_velocities_ref: Sequence[float] | None = None,
        dt: float = 0.0,
    ) -> JointPIResult:
        result = self.compute(
            joints_positions=joints_positions,
            joints_positions_ref=joints_positions_ref,
            joints_velocities_ref=joints_velocities_ref,
            dt=dt,
            integral_state=self._integral_state,
        )
        self._integral_state = result.next_integral_state
        return result

    @staticmethod
    def _normalize_gain(
        gain: Real | Sequence[float] | Sequence[Sequence[float]] | np.ndarray,
        joints_count: int,
        gain_name: str,
    ) -> np.ndarray:
        if isinstance(gain, Real):
            scalar_gain = float(gain)
            return np.eye(joints_count, dtype=float) * scalar_gain

        if isinstance(gain, (str, bytes)):
            raise ValueError(f"`{gain_name}` must contain numeric values.") from None

        try:
            gain_array = np.asarray(gain, dtype=float)
        except (TypeError, ValueError):
            raise ValueError(f"`{gain_name}` must contain numeric values.") from None

        if gain_array.ndim == 0:
            scalar_gain = float(gain_array.item())
            return np.eye(joints_count, dtype=float) * scalar_gain

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
            return np.diag(np.diag(gain_array))

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
