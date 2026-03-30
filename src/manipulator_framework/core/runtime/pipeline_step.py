from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types.execution import StepResult
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
