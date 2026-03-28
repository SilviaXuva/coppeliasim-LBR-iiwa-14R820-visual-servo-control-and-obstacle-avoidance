from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import ResultsRepositoryInterface
from manipulator_framework.core.experiments import RunResult


@dataclass
class ExperimentService:
    """
    Application service for storing experiment results.
    """
    results_repository: ResultsRepositoryInterface

    def persist(self, result: RunResult) -> None:
        self.results_repository.save_result(result)
