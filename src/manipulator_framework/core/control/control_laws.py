from __future__ import annotations

import numpy as np


def compute_pi_control(
    position_error: np.ndarray,
    integral_error: np.ndarray,
    kp: np.ndarray,
    ki: np.ndarray,
) -> np.ndarray:
    return kp * position_error + ki * integral_error


def compute_pd_control(
    position_error: np.ndarray,
    velocity_error: np.ndarray,
    kp: np.ndarray,
    kd: np.ndarray,
) -> np.ndarray:
    return kp * position_error + kd * velocity_error


def compute_adaptive_pd_control(
    position_error: np.ndarray,
    velocity_error: np.ndarray,
    kp: np.ndarray,
    kd: np.ndarray,
    adaptive_bias: np.ndarray,
) -> np.ndarray:
    return kp * position_error + kd * velocity_error + adaptive_bias
