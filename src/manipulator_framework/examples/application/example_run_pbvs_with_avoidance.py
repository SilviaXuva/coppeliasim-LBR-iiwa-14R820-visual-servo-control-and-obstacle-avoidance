from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from manipulator_framework.examples.application._mocks import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def main() -> None:
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=InMemoryResultsRepository(),
    )

    use_case = composer.build_run_pbvs_with_avoidance()
    response = use_case.execute(
        RunPBVSWithAvoidanceRequest(
            run_id="run_pbvs_avoidance_001",
            config={"backend_name": "mock", "scenario_name": "pbvs_with_avoidance"},
            seed=99,
            duration=1.0,
        )
    )

    print(response.run_result)


if __name__ == "__main__":
    main()
