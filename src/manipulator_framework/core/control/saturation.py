from __future__ import annotations

import numpy as np


def clip_vector(values: np.ndarray, lower: np.ndarray | float, upper: np.ndarray | float) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return np.clip(arr, lower, upper)


def symmetric_clip(values: np.ndarray, limit: np.ndarray | float) -> np.ndarray:
    lim = np.asarray(limit, dtype=float)
    return np.clip(np.asarray(values, dtype=float), -lim, lim)
