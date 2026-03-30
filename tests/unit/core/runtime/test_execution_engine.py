from __future__ import annotations

from manipulator_framework.core.runtime import (
    ActuationStep,
    ControlStep,
    EstimationStep,
    ExecutionEngine,
    PlanningStep,
    RuntimePipeline,
    SensingStep,
)
from tests.fixtures.application_fakes import (
    FakeCamera,
    FakeClock,
    FakeController,
    FakePersonDetector,
    FakePoseEstimator,
    FakePlanner,
    FakeRobot,
    FakeTracker,
)


def test_execution_engine_runs_one_cycle_successfully() -> None:
    engine = ExecutionEngine(
        clock=FakeClock(),
        pipeline=RuntimePipeline(
            steps=[
                SensingStep(robot=FakeRobot(), camera=FakeCamera()),
                EstimationStep(
                    person_detector=FakePersonDetector(),
                    target_estimator=FakePoseEstimator(),
                    tracker=FakeTracker(),
                ),
                PlanningStep(planner=FakePlanner()),
                ControlStep(controller=FakeController(), dt=0.1),
                ActuationStep(robot=FakeRobot()),
            ]
        ),
    )

    result = engine.step()

    assert result.success is True
    assert len(result.events) == 5


def test_execution_engine_respects_sampling_period_in_run_loop() -> None:
    engine = ExecutionEngine(
        clock=FakeClock(start_time=2.0, step_dt=0.1),
        pipeline=RuntimePipeline(
            steps=[
                SensingStep(robot=FakeRobot(), camera=FakeCamera()),
            ]
        ),
        sampling_period_s=0.2,
    )

    run_result = engine.run(
        run_id="sampling_period_test",
        resolved_config={},
        seed=1,
        num_cycles=3,
        start_time=2.0,
    )

    assert tuple(cycle.timestamp for cycle in run_result.cycle_results) == (2.0, 2.2, 2.4)
    assert run_result.summary["sampling_period_s"] == 0.2
    assert run_result.summary["sampling_frequency_hz"] == 5.0
