from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Real


@dataclass(slots=True, frozen=True)
class JointPIResult:
    joints_velocities: tuple[float, ...]
    error: tuple[float, ...]
    next_integral_state: tuple[float, ...]


class JointPIController:
    """
    Joint-space PI controller equivalent to legacy JointSpaceController.

    Legacy behavior preserved:
    - integral state is the previous joint error
    - command = Kp*e + Ki*(int_state + e*dt) + q_dot_ref
    """

    def __init__(
        self,
        kp: float | Sequence[float],
        ki: float | Sequence[float],
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
        joints_velocities_ref: Sequence[float] | None = None,
        dt: float = 0.0,
        integral_state: Sequence[float] | None = None,
    ) -> JointPIResult:
        if dt < 0.0:
            raise ValueError("`dt` must be non-negative.")

        q = self._as_vector(joints_positions, self._joints_count, "joints_positions")
        q_ref = self._as_vector(
            joints_positions_ref, self._joints_count, "joints_positions_ref"
        )
        if joints_velocities_ref is None:
            q_dot_ref = tuple(0.0 for _ in range(self._joints_count))
        else:
            q_dot_ref = self._as_vector(
                joints_velocities_ref,
                self._joints_count,
                "joints_velocities_ref",
            )

        if integral_state is None:
            int_state = self._integral_state
        else:
            int_state = self._as_vector(
                integral_state, self._joints_count, "integral_state"
            )

        error = tuple(q_ref_i - q_i for q_ref_i, q_i in zip(q_ref, q))
        control = tuple(
            self._kp[i] * error[i]
            + self._ki[i] * (int_state[i] + error[i] * dt)
            + q_dot_ref[i]
            for i in range(self._joints_count)
        )

        return JointPIResult(
            joints_velocities=control,
            error=error,
            next_integral_state=error,
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
        gain: float | Sequence[float],
        joints_count: int,
        gain_name: str,
    ) -> tuple[float, ...]:
        if isinstance(gain, Real):
            scalar_gain = float(gain)
            return tuple(scalar_gain for _ in range(joints_count))

        gain_values = tuple(gain)
        if len(gain_values) == joints_count:
            try:
                return tuple(float(value) for value in gain_values)
            except (TypeError, ValueError):
                pass

        if len(gain_values) == joints_count:
            rows = []
            for row in gain_values:
                if isinstance(row, (str, bytes)):
                    raise ValueError(
                        f"`{gain_name}` matrix must contain numeric values."
                    ) from None
                try:
                    rows.append(tuple(float(value) for value in row))  # type: ignore[arg-type]
                except (TypeError, ValueError):
                    raise ValueError(
                        f"`{gain_name}` matrix must contain numeric values."
                    ) from None
            if any(len(row) != joints_count for row in rows):
                raise ValueError(
                    f"`{gain_name}` matrix must be {joints_count}x{joints_count}."
                )
            return tuple(row[i] for i, row in enumerate(rows))

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
