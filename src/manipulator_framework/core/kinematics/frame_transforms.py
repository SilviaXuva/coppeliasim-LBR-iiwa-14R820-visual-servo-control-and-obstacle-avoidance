from __future__ import annotations

import numpy as np


def invert_transform(T_ab: np.ndarray) -> np.ndarray:
    T = np.asarray(T_ab, dtype=float)
    if T.shape != (4, 4):
        raise ValueError("Transform must have shape (4, 4).")

    R = T[:3, :3]
    p = T[:3, 3]

    T_ba = np.eye(4, dtype=float)
    T_ba[:3, :3] = R.T
    T_ba[:3, 3] = -R.T @ p
    return T_ba


def compose_transforms(T_ab: np.ndarray, T_bc: np.ndarray) -> np.ndarray:
    A = np.asarray(T_ab, dtype=float)
    B = np.asarray(T_bc, dtype=float)
    if A.shape != (4, 4) or B.shape != (4, 4):
        raise ValueError("Both transforms must have shape (4, 4).")
    return A @ B
