from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import ControllerInterface
from .cycle_contract import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class ControlStep(PipelineStep):
    controller: ControllerInterface
    dt: float

    @property
    def name(self) -> str:
        return "control"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.robot_state is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Robot state is required before control.",
                timestamp=context.timestamp,
            )

        if context.trajectory_reference is None or not context.trajectory_reference.samples:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Trajectory reference is required before control.",
                timestamp=context.timestamp,
            )

        reference_sample = context.trajectory_reference.samples[-1]
        context.control_output = self.controller.compute_control(
            robot_state=context.robot_state,
            reference=reference_sample,
            dt=self.dt,
        )

        return StepResult(
            step_name=self.name,
            success=True,
            message="Control step completed.",
            timestamp=context.timestamp,
        )
