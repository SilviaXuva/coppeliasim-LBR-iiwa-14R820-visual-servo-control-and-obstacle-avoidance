from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .constants import DEG_TO_RAD


@dataclass(frozen=True)
class JointLimits:
    lower: np.ndarray
    upper: np.ndarray

    def contains(self, q: np.ndarray) -> bool:
        q_arr = np.asarray(q, dtype=float).reshape(-1)
        return bool(np.all(q_arr >= self.lower) and np.all(q_arr <= self.upper))


@dataclass(frozen=True)
class TorqueLimits:
    lower: np.ndarray
    upper: np.ndarray


def get_iiwa14r820_joint_limits() -> JointLimits:
    lower_deg = np.array([-170.0, -120.0, -170.0, -120.0, -170.0, -120.0, -175.0])
    upper_deg = np.array([170.0, 120.0, 170.0, 120.0, 170.0, 120.0, 175.0])

    return JointLimits(
        lower=lower_deg * DEG_TO_RAD,
        upper=upper_deg * DEG_TO_RAD,
    )


def get_iiwa14r820_torque_limits() -> TorqueLimits:
    upper = np.array([176.0, 176.0, 100.0, 100.0, 100.0, 38.0, 38.0], dtype=float)
    return TorqueLimits(lower=-upper, upper=upper)
