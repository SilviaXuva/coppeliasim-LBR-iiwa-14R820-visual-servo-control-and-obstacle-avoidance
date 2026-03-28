from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.examples.application._mocks import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def test_mock_composer_builds_main_use_cases() -> None:
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=InMemoryResultsRepository(),
    )

    assert composer.build_run_joint_trajectory() is not None
    assert composer.build_run_pbvs() is not None
    assert composer.build_run_pbvs_with_tracking() is not None
    assert composer.build_run_pbvs_with_avoidance() is not None
    assert composer.build_benchmark_controllers() is not None
