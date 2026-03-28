from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import PersonDetectorInterface, TrackerInterface
from .cycle_contract import StepResult
from .pipeline_step import PipelineStep
from .runtime_context import RuntimeContext


@dataclass
class EstimationStep(PipelineStep):
    person_detector: PersonDetectorInterface
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
        context.tracked_targets = list(self.tracker.update(context.person_detections, context.timestamp))

        return StepResult(
            step_name=self.name,
            success=True,
            message="Estimation step completed.",
            timestamp=context.timestamp,
        )
