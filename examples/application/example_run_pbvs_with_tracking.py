from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import RunPBVSWithTrackingRequest
from examples.application._mocks import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def main() -> None:
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=InMemoryResultsRepository(),
    )

    use_case = composer.build_run_pbvs_with_tracking()
    response = use_case.execute(
        RunPBVSWithTrackingRequest(
            run_id="run_pbvs_tracking_001",
            config={"backend_name": "mock", "scenario_name": "pbvs_with_tracking"},
            seed=13,
            duration=1.0,
        )
    )

    print(response.run_result)


if __name__ == "__main__":
    main()
