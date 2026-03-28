from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import RobotInterface
from .cycle_contract import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class ActuationStep(PipelineStep):
    robot: RobotInterface

    @property
    def name(self) -> str:
        return "actuation"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.control_output is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Control output is required before actuation.",
                timestamp=context.timestamp,
            )

        if context.control_output.joint_command is not None:
            self.robot.send_joint_command(context.control_output.joint_command)

        return StepResult(
            step_name=self.name,
            success=True,
            message="Actuation step completed.",
            timestamp=context.timestamp,
        )
