from __future__ import annotations

from dataclasses import dataclass, field

from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class RuntimePipeline:
    """
    Ordered collection of runtime steps.
    """
    steps: list[PipelineStep] = field(default_factory=list)

    def run_cycle(self, context: RuntimeContext) -> tuple[StepResult, ...]:
        results: list[StepResult] = []

        for step in self.steps:
            result = step.run(context)
            results.append(result)

            if not result.success:
                break

        return tuple(results)
