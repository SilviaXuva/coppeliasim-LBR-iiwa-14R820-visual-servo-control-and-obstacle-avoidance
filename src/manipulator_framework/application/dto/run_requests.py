from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RunRequest:
    """
    Base application request.
    """
    run_id: str
    config: dict[str, Any]
    seed: int = 0


@dataclass(frozen=True)
class RunJointTrajectoryRequest(RunRequest):
    duration: float = 1.0


@dataclass(frozen=True)
class RunPBVSRequest(RunRequest):
    duration: float = 1.0


@dataclass(frozen=True)
class RunPBVSWithTrackingRequest(RunRequest):
    duration: float = 1.0


@dataclass(frozen=True)
class RunPBVSWithAvoidanceRequest(RunRequest):
    duration: float = 1.0


@dataclass(frozen=True)
class BenchmarkControllersRequest(RunRequest):
    compared_methods: tuple[str, ...] = ()
    repetitions: int = 1
