from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import (
    ObstacleAvoidanceInterface,
    ObstacleSourceInterface,
)
from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class AvoidanceStep(PipelineStep):
    """
    Step that adapts a trajectory according to obstacle information.
    This handles the 'aplicar avoidance' requirement of the loop.
    """
    avoidance_module: ObstacleAvoidanceInterface
    obstacle_source: ObstacleSourceInterface | None = None

    @property
    def name(self) -> str:
        return "avoidance"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.robot_state is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Robot state is required for obstacle avoidance.",
                timestamp=context.timestamp,
            )

        if context.trajectory_reference is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Trajectory reference is required before avoidance.",
                timestamp=context.timestamp,
            )

        # 1. Update Obstacles
        if self.obstacle_source is not None:
             context.obstacles = self.obstacle_source.get_obstacles()

        # 2. Adaptation
        context.trajectory_reference = self.avoidance_module.adapt_trajectory(
            reference=context.trajectory_reference,
            obstacles=context.obstacles,
            robot_state=context.robot_state,
        )

        return StepResult(
            step_name=self.name,
            success=True,
            message=f"Avoidance adaptation completed. Obstacles monitored: {len(context.obstacles)}",
            timestamp=context.timestamp,
        )
