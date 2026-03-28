from __future__ import annotations

from abc import ABC, abstractmethod

from .cycle_contract import StepResult
from .runtime_context import RuntimeContext


class PipelineStep(ABC):
    """
    Base contract for a runtime pipeline step.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self, context: RuntimeContext) -> StepResult:
        raise NotImplementedError
