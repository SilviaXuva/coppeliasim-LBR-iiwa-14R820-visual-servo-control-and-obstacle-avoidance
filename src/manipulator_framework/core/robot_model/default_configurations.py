from __future__ import annotations

import numpy as np

from .constants import DEG_TO_RAD


def get_qz() -> np.ndarray:
    """Return the zero joint configuration."""
    return np.zeros(7, dtype=float)


def get_qr() -> np.ndarray:
    """Return the ready joint configuration."""
    return np.array([0.0, 0.0, 0.0, 90.0, 0.0, -90.0, 90.0], dtype=float) * DEG_TO_RAD
