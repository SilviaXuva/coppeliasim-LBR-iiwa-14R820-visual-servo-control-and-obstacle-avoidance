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


def test_fake_runtime_cycle_sends_command_to_robot() -> None:
    robot = FakeRobot()

    engine = ExecutionEngine(
        clock=FakeClock(),
        pipeline=RuntimePipeline(
            steps=[
                SensingStep(robot=robot, camera=FakeCamera()),
                EstimationStep(
                    person_detector=FakePersonDetector(),
                    target_estimator=FakePoseEstimator(),
                    tracker=FakeTracker(),
                ),
                PlanningStep(planner=FakePlanner()),
                ControlStep(controller=FakeController(), dt=0.1),
                ActuationStep(robot=robot),
            ]
        ),
    )

    result = engine.step()

    assert result.success is True
    assert robot.last_command is not None
