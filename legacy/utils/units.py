import numpy as np

DEG_TO_RAD = np.pi / 180
RAD_TO_DEG = 180 / np.pi

CM_TO_M = 1e-2
MM_TO_M = 1e-3

G_TO_KG = 1e-3
MS_TO_S = 1e-3


def deg2rad(x):
    """Convert degrees to radians."""
    return x * DEG_TO_RAD


def rad2deg(x):
    """Convert radians to degrees."""
    return x * RAD_TO_DEG


__all__ = [
    "DEG_TO_RAD",
    "RAD_TO_DEG",
    "CM_TO_M",
    "MM_TO_M",
    "G_TO_KG",
    "MS_TO_S",
    "deg2rad",
    "rad2deg",
]
