from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import ObstacleState


@dataclass(frozen=True)
class AvoidanceCandidate:
    """
    Candidate joint-space offset used by the avoidance search.
    """
    delta_q: np.ndarray


@dataclass(frozen=True)
class AvoidanceResult:
    """
    Result of obstacle avoidance adaptation.
    """
    best_delta_q: np.ndarray
    best_cost: float
    is_safe: bool
