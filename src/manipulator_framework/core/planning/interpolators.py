from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.types import Trajectory, TrajectorySample


@dataclass(frozen=True)
class NearestSampleInterpolator:
    """
    Minimal discrete interpolator for already-sampled trajectories.

    Placeholder:
        This is intentionally simple and discrete.
        Continuous interpolation can be introduced later without changing the trajectory contract.
    """

    trajectory: Trajectory

    def sample(self, t: float) -> TrajectorySample:
        closest = min(self.trajectory.samples, key=lambda s: abs(s.time_from_start - t))
        return closest
