from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(slots=True)
class TrajectorySample:
    """
    Base sample for a time-parameterized trajectory.

    Attributes
    ----------
    t : float
        Global time [s].
    s : float
        Normalized path position in [0, 1].
    ds : float
        Time derivative of normalized path position [1/s].
    dds : float
        Second time derivative of normalized path position [1/s²].
    done : bool
        Whether the trajectory has reached its final time.
    """

    t: float
    s: float
    ds: float
    dds: float
    done: bool


@dataclass(slots=True)
class JointTrajectorySample(TrajectorySample):
    """
    Sample of a joint-space trajectory.

    Attributes
    ----------
    q : np.ndarray
        Joint positions.
    dq : np.ndarray
        Joint velocities.
    ddq : np.ndarray
        Joint accelerations.
    """

    q: np.ndarray
    dq: np.ndarray
    ddq: np.ndarray


class TimeScalingProfile(Protocol):
    """
    Protocol for normalized time-scaling profiles.
    """

    def evaluate(self, tau: float, duration: float) -> tuple[float, float, float]:
        """
        Evaluate the normalized profile.

        Parameters
        ----------
        tau : float
            Local trajectory time [s], typically in [0, duration].
        duration : float
            Total trajectory duration [s].

        Returns
        -------
        tuple[float, float, float]
            s, ds, dds
        """
        ...
