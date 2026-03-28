from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import RunPBVSRequest
from manipulator_framework.examples.application._mocks import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def test_run_pbvs_returns_run_result() -> None:
    repository = InMemoryResultsRepository()
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=repository,
    )

    use_case = composer.build_run_pbvs()
    response = use_case.execute(
        RunPBVSRequest(
            run_id="pbvs_001",
            config={"backend_name": "mock", "scenario_name": "pbvs_synthetic_target"},
            seed=2,
            duration=1.0,
        )
    )

    assert response.run_result.success is True
    assert response.run_result.run_schema.experiment_name == "run_pbvs"
