from __future__ import annotations

from manipulator_framework.core.runtime import (
    ActuationStep,
    ControlStep,
    EstimationStep,
    PlanningStep,
    RuntimeContext,
    SensingStep,
)
from examples.core.runtime._mocks import (
    FakeCamera,
    FakeController,
    FakePersonDetector,
    FakePlanner,
    FakeRobot,
    FakeTracker,
)


def test_pipeline_steps_run_in_expected_order() -> None:
    robot = FakeRobot()
    context = RuntimeContext(cycle_index=0, timestamp=0.1)

    sensing = SensingStep(robot=robot, camera=FakeCamera())
    estimation = EstimationStep(person_detector=FakePersonDetector(), tracker=FakeTracker())
    planning = PlanningStep(planner=FakePlanner())
    control = ControlStep(controller=FakeController(), dt=0.1)
    actuation = ActuationStep(robot=robot)

    assert sensing.run(context).success is True
    assert estimation.run(context).success is True
    assert planning.run(context).success is True
    assert control.run(context).success is True
    assert actuation.run(context).success is True
