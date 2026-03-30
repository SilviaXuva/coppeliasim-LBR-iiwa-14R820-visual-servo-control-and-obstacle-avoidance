from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import RunJointTrajectoryRequest
from manipulator_framework.core.runtime import ExecutionEngine, RuntimePipeline, StepResult
from manipulator_framework.core.runtime.pipeline_step import PipelineStep
from manipulator_framework.core.runtime.runtime_context import RuntimeContext
from tests.fixtures.application_fakes import FakeClock, InMemoryResultsRepository


@dataclass
class _SuccessfulStep(PipelineStep):
    step_label: str

    @property
    def name(self) -> str:
        return self.step_label

    def run(self, context: RuntimeContext) -> StepResult:
        context.metadata[self.step_label] = "ok"
        return StepResult(
            step_name=self.step_label,
            success=True,
            message=f"{self.step_label} completed.",
            timestamp=context.timestamp,
        )


@dataclass
class _FailingStep(PipelineStep):
    step_label: str

    @property
    def name(self) -> str:
        return self.step_label

    def run(self, context: RuntimeContext) -> StepResult:
        return StepResult(
            step_name=self.step_label,
            success=False,
            message=f"{self.step_label} failed.",
            timestamp=context.timestamp,
        )


def test_execution_engine_real_pipeline_returns_cycle_result_object() -> None:
    engine = ExecutionEngine(
        clock=FakeClock(start_time=10.0, step_dt=0.1),
        pipeline=RuntimePipeline(
            steps=[
                _SuccessfulStep("sensing"),
                _SuccessfulStep("planning"),
                _SuccessfulStep("control"),
            ]
        ),
    )

    cycle_result = engine.step()

    assert cycle_result.cycle_index == 0
    assert cycle_result.success is True
    assert cycle_result.timestamp == 10.0
    assert len(cycle_result.events) == 3
    assert tuple(event.split(":")[0] for event in cycle_result.events) == (
        "sensing",
        "planning",
        "control",
    )


def test_execution_engine_stops_pipeline_after_first_failure() -> None:
    engine = ExecutionEngine(
        clock=FakeClock(start_time=20.0, step_dt=0.1),
        pipeline=RuntimePipeline(
            steps=[
                _SuccessfulStep("sensing"),
                _FailingStep("planning"),
                _SuccessfulStep("control"),
            ]
        ),
    )

    cycle_result = engine.step()

    assert cycle_result.cycle_index == 0
    assert cycle_result.success is False
    assert len(cycle_result.events) == 2
    assert tuple(event.split(":")[0] for event in cycle_result.events) == (
        "sensing",
        "planning",
    )
    assert cycle_result.errors[-1] == "planning failed."


def test_run_joint_trajectory_with_real_execution_engine_persists_run_result() -> None:
    repository = InMemoryResultsRepository()
    engine = ExecutionEngine(
        clock=FakeClock(start_time=30.0, step_dt=0.1),
        pipeline=RuntimePipeline(
            steps=[
                _SuccessfulStep("sensing"),
                _SuccessfulStep("planning"),
                _SuccessfulStep("control"),
            ]
        ),
    )
    composer = MockApplicationComposer(
        clock=FakeClock(start_time=30.0, step_dt=0.1),
        execution_engine=engine,
        results_repository=repository,
    )

    use_case = composer.build_run_joint_trajectory()
    response = use_case.execute(
        RunJointTrajectoryRequest(
            run_id="integration_contract_001",
            config={
                "backend_name": "mock",
                "scenario_name": "synthetic_joint_trajectory",
            },
            seed=123,
            duration=1.0,
        )
    )

    assert response.run_result.success is True
    assert response.run_result.summary["experiment_name"] == "run_joint_trajectory"
    assert response.run_result.summary["final_cycle_index"] == 9
    assert len(repository.saved_results) == 1
    assert repository.saved_results[0] == response.run_result
