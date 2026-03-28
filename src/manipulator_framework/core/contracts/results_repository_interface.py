from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from manipulator_framework.core.types import ExperimentResult


class ResultsRepositoryInterface(ABC):
    """Persist experimental outputs."""

    @abstractmethod
    def save_result(self, result: ExperimentResult) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_timeseries(self, run_id: str, series_name: str, samples: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_artifact(self, run_id: str, artifact_name: str, artifact_path: str) -> None:
        raise NotImplementedError
