from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import PlannerInterface
from .cycle_contract import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class PlanningStep(PipelineStep):
    planner: PlannerInterface

    @property
    def name(self) -> str:
        return "planning"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.robot_state is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Robot state is required before planning.",
                timestamp=context.timestamp,
            )

        context.trajectory_reference = self.planner.plan(
            robot_state=context.robot_state,
            tracked_targets=context.tracked_targets,
        )

        return StepResult(
            step_name=self.name,
            success=True,
            message="Planning step completed.",
            timestamp=context.timestamp,
        )
