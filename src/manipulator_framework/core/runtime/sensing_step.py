from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import CameraInterface, RobotInterface
from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class SensingStep(PipelineStep):
    robot: RobotInterface
    camera: CameraInterface | None = None

    @property
    def name(self) -> str:
        return "sensing"

    def run(self, context: RuntimeContext) -> StepResult:
        context.robot_state = self.robot.get_robot_state()

        if self.camera is not None:
            context.camera_frame = self.camera.get_frame()

        return StepResult(
            step_name=self.name,
            success=True,
            message="Sensing step completed.",
            timestamp=context.timestamp,
        )
