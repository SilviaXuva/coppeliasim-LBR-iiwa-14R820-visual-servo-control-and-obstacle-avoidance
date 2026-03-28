from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from tests.fixtures.application_fakes import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def test_run_pbvs_with_avoidance_returns_run_result() -> None:
    repository = InMemoryResultsRepository()
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=repository,
    )

    use_case = composer.build_run_pbvs_with_avoidance()
    response = use_case.execute(
        RunPBVSWithAvoidanceRequest(
            run_id="pbvs_avoidance_001",
            config={"backend_name": "mock", "scenario_name": "pbvs_with_avoidance"},
            seed=4,
            duration=1.0,
        )
    )

    assert response.run_result.success is True
    assert response.run_result.run_schema.experiment_name == "run_pbvs_with_avoidance"
