from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import RunJointTrajectoryRequest
from manipulator_framework.core.runtime import CycleResult
from tests.fixtures.application_fakes import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def test_fake_execution_engine_returns_cycle_result() -> None:
    engine = FakeExecutionEngine()

    result = engine.step()

    assert isinstance(result, CycleResult)
    assert result.success is True
    assert result.cycle_index == 0
    assert len(result.step_results) == 3


def test_use_case_consumes_cycle_result_object_contract() -> None:
    repository = InMemoryResultsRepository()
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=repository,
    )

    use_case = composer.build_run_joint_trajectory()
    response = use_case.execute(
        RunJointTrajectoryRequest(
            run_id="contract_alignment_001",
            config={
                "backend_name": "mock",
                "scenario_name": "synthetic_joint_trajectory",
            },
            seed=123,
            duration=1.0,
        )
    )

    assert response.run_result.success is True
    assert response.execution_plan.num_cycles == 10
    assert len(response.cycle_results) == 10
    assert response.cycle_result.cycle_index == 9
    assert response.run_result.metadata["final_cycle_index"] == 9
    assert response.run_result.metadata["num_cycles"] == 10
    assert len(repository.saved_results) == 1
