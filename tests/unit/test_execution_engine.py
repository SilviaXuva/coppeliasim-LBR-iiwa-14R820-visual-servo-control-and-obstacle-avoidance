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
from examples.runtime._mocks import (
    FakeCamera,
    FakeClock,
    FakeController,
    FakePersonDetector,
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
                EstimationStep(person_detector=FakePersonDetector(), tracker=FakeTracker()),
                PlanningStep(planner=FakePlanner()),
                ControlStep(controller=FakeController(), dt=0.1),
                ActuationStep(robot=FakeRobot()),
            ]
        ),
    )

    result = engine.step()

    assert result.success is True
    assert len(result.step_results) == 5
