from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import (
    PersonDetectorInterface,
    PoseEstimatorInterface,
    TrackerInterface,
)
from manipulator_framework.core.types.execution import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class EstimationStep(PipelineStep):
    person_detector: PersonDetectorInterface
    target_estimator: PoseEstimatorInterface
    tracker: TrackerInterface

    @property
    def name(self) -> str:
        return "estimation"

    def run(self, context: RuntimeContext) -> StepResult:
        if context.camera_frame is None:
            return StepResult(
                step_name=self.name,
                success=False,
                message="Camera frame is required before estimation.",
                timestamp=context.timestamp,
            )

        context.person_detections = list(self.person_detector.detect_people(context.camera_frame))
        estimated_targets = [
            target
            for target in (
                self.target_estimator.estimate_person_target(detection)
                for detection in context.person_detections
            )
            if target is not None
        ]
        context.tracked_targets = list(self.tracker.update(estimated_targets, context.timestamp))

        return StepResult(
            step_name=self.name,
            success=True,
            message="Estimation step completed.",
            timestamp=context.timestamp,
        )
