from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import MarkerDetectorInterface, PoseEstimatorInterface
from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class PerceptionStep(PipelineStep):
    """
    Step that converts visual frames into detected semantic objects and their poses.
    This fulfills the 'detect target' and 'estimate pose' requirements of the loop.
    """
    marker_detector: MarkerDetectorInterface
    pose_estimator: PoseEstimatorInterface

    @property
    def name(self) -> str:
        return "perception"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.camera_frame is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Camera frame is required before perception.",
                timestamp=context.timestamp,
            )

        # 1. Detection
        context.marker_detections = self.marker_detector.detect_markers(context.camera_frame)
        
        # 2. Pose Estimation (Primary target)
        if context.marker_detections:
            # For simplicity, we estimate the pose of the first detected marker
            primary_marker = context.marker_detections[0]
            context.target_pose = self.pose_estimator.estimate_marker_pose(primary_marker)

        return StepResult(
            step_name=self.name,
            success=True,
            message=f"Perception completed. Markers detected: {len(context.marker_detections)}",
            timestamp=context.timestamp,
        )
