from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.metrics import (
    compute_joint_error,
    compute_success_from_visual_error,
    compute_visual_servo_error,
)
from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class MetricsStep(PipelineStep):
    """
    Step that collects cycle-level scientific metrics and stores them in context metadata.
    """

    visual_success_threshold: float = 0.02

    @property
    def name(self) -> str:
        return "metrics_collection"

    def run(self, context: RuntimeContext) -> StepResult:
        metrics: dict[str, float] = {}

        if context.marker_detections:
            metrics["num_markers_detected"] = float(len(context.marker_detections))

        if "visual_error" in context.metadata:
            error = context.metadata["visual_error"]
            translation_error = getattr(error, "translation_error", None)
            rotation_error = getattr(error, "rotation_error", None)
            if isinstance(translation_error, (int, float)):
                metrics["visual_translation_error"] = float(translation_error)
            if isinstance(rotation_error, (int, float)):
                metrics["visual_rotation_error"] = float(rotation_error)

        if (
            context.target_pose is not None
            and context.robot_state is not None
            and context.robot_state.end_effector_pose is not None
        ):
            visual_error_metric = compute_visual_servo_error(
                target_pose=context.target_pose,
                ee_pose=context.robot_state.end_effector_pose,
            )
            metrics[visual_error_metric.name] = float(visual_error_metric.value)
            success_metric = compute_success_from_visual_error(
                visual_error=visual_error_metric.value,
                threshold=self.visual_success_threshold,
            )
            metrics[success_metric.name] = float(success_metric.value)

        if (
            context.trajectory_reference is not None
            and context.trajectory_reference.samples
            and context.robot_state is not None
        ):
            desired_joint_state = context.trajectory_reference.samples[-1].joint_state
            actual_joint_state = context.robot_state.joint_state
            joint_error_metric = compute_joint_error(
                q_desired=desired_joint_state,
                q_actual=actual_joint_state,
            )
            metrics[joint_error_metric.name] = float(joint_error_metric.value)

        if context.obstacles:
            metrics["num_obstacles"] = float(len(context.obstacles))
            if context.robot_state is not None and context.robot_state.end_effector_pose is not None:
                ee = np.asarray(context.robot_state.end_effector_pose.position, dtype=float)
                clearance_samples: list[float] = []
                for obstacle in context.obstacles:
                    obs = np.asarray(obstacle.pose.position, dtype=float)
                    radius = float(obstacle.radius or 0.0)
                    clearance_samples.append(float(np.linalg.norm(ee - obs)) - radius)
                if clearance_samples:
                    metrics["minimum_clearance"] = min(clearance_samples)

        context.metadata["cycle_metrics"] = dict(metrics)

        return StepResult(
            step_name=self.name,
            success=True,
            message=f"Metrics collected for cycle {context.cycle_index}.",
            timestamp=context.timestamp,
        )
