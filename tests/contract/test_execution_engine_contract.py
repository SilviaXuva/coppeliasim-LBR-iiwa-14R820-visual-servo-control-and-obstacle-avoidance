from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.runtime import CycleResult, ExecutionEngine, RuntimePipeline, StepResult
from manipulator_framework.core.runtime.pipeline_step import PipelineStep
from manipulator_framework.core.runtime.runtime_context import RuntimeContext
from tests.fixtures.application_fakes import FakeClock, FakeExecutionEngine


@dataclass
class _SuccessfulStep(PipelineStep):
    step_label: str

    @property
    def name(self) -> str:
        return self.step_label

    def run(self, context: RuntimeContext) -> StepResult:
        return StepResult(
            step_name=self.step_label,
            success=True,
            message=f"{self.step_label} executed.",
            timestamp=context.timestamp,
        )


def test_fake_execution_engine_matches_concrete_step_contract() -> None:
    fake_engine = FakeExecutionEngine(
        step_names=("sensing", "planning", "control"),
        success=True,
    )
    concrete_engine = ExecutionEngine(
        clock=FakeClock(start_time=0.0, step_dt=0.1),
        pipeline=RuntimePipeline(
            steps=[
                _SuccessfulStep("sensing"),
                _SuccessfulStep("planning"),
                _SuccessfulStep("control"),
            ]
        ),
    )

    fake_result = fake_engine.step()
    concrete_result = concrete_engine.step()

    assert isinstance(fake_result, CycleResult)
    assert isinstance(concrete_result, CycleResult)

    assert fake_result.success is True
    assert concrete_result.success is True

    assert fake_result.cycle_index == 0
    assert concrete_result.cycle_index == 0

    assert all(isinstance(item, StepResult) for item in fake_result.step_results)
    assert all(isinstance(item, StepResult) for item in concrete_result.step_results)

    assert tuple(item.step_name for item in fake_result.step_results) == (
        "sensing",
        "planning",
        "control",
    )
    assert tuple(item.step_name for item in concrete_result.step_results) == (
        "sensing",
        "planning",
        "control",
    )
