from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.experiments import RunResult


class ResultsRepositoryInterface(ABC):
    """
    Persistence contract for all experimental and application outputs.
    Ensures scientific reproducibility and traceability across backends.
    """

    @abstractmethod
    def save_run(self, result: RunResult) -> None:
        """Persist the canonical RunResult."""
        raise NotImplementedError
