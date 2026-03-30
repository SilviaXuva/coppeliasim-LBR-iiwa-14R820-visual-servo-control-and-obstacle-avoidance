from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import SimulatorInterface
from manipulator_framework.core.types.execution import StepResult

from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class SimulatorStep(PipelineStep):
    simulator: SimulatorInterface

    @property
    def name(self) -> str:
        return "simulator"

    def run(self, context: RuntimeContext) -> StepResult:
        self.simulator.step()
        return StepResult(
            step_name=self.name,
            success=True,
            message="Simulator step completed.",
            timestamp=context.timestamp,
        )
