from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.runtime import (
    ExecutionEngine,
    PipelineStep,
    RuntimeContext,
    RuntimePipeline,
    StepResult,
)

from manipulator_framework.examples.core.runtime._mocks import (
    FakeCamera,
    FakeClock,
    FakeController,
    FakePersonDetector,
    FakePlanner,
    FakeRobot,
    FakeTracker,
)


@dataclass
class AlwaysFailStep(PipelineStep):
    @property
    def name(self) -> str:
        return "always_fail"

    def run(self, context: RuntimeContext) -> StepResult:
        return StepResult(
            step_name=self.name,
            success=False,
            message="Intentional failure for runtime contract validation.",
            timestamp=context.timestamp,
        )


def main() -> None:
    pipeline = RuntimePipeline(steps=[AlwaysFailStep()])
    engine = ExecutionEngine(clock=FakeClock(), pipeline=pipeline)

    result = engine.step()
    print(result)


if __name__ == "__main__":
    main()
