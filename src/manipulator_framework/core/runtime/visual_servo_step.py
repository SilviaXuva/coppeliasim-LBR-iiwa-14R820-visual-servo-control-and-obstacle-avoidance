from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import VisualServoInterface
from manipulator_framework.core.types import Pose3D
from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class VisualServoStep(PipelineStep):
    """
    Step that computes a trajectory reference from visual information (PBVS).
    This handles the 'calcular comando PBVS' requirement of the loop.
    """
    pbvs_controller: VisualServoInterface
    desired_target_pose: Pose3D
    dt: float = 0.01

    @property
    def name(self) -> str:
        return "visual_servo"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.robot_state is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Robot state is required for visual servoing.",
                timestamp=context.timestamp,
            )

        if context.target_pose is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Current target pose is required for visual servoing.",
                timestamp=context.timestamp,
            )

        # 1. Compute Reference (Trajectory)
        visual_error, trajectory = self.pbvs_controller.compute_reference(
            robot_state=context.robot_state,
            current_target_pose=context.target_pose,
            desired_target_pose=self.desired_target_pose,
            dt=self.dt,
        )

        # 2. Store in Context
        context.trajectory_reference = trajectory
        context.metadata["visual_error"] = visual_error

        return StepResult(
            step_name=self.name,
            success=True,
            message=f"Visual servoing reference computed. Position error: {visual_error.translation_error:.3f}m.",
            timestamp=context.timestamp,
        )
