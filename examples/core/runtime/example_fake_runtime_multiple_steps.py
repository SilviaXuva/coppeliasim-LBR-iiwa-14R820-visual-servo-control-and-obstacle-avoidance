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

from examples.core.runtime._mocks import (
    FakeCamera,
    FakeClock,
    FakeController,
    FakePersonDetector,
    FakePlanner,
    FakeRobot,
    FakeTracker,
)


def main() -> None:
    robot = FakeRobot()
    engine = ExecutionEngine(
        clock=FakeClock(),
        pipeline=RuntimePipeline(
            steps=[
                SensingStep(robot=robot, camera=FakeCamera()),
                EstimationStep(person_detector=FakePersonDetector(), tracker=FakeTracker()),
                PlanningStep(planner=FakePlanner()),
                ControlStep(controller=FakeController(), dt=0.1),
                ActuationStep(robot=robot),
            ]
        ),
    )

    for _ in range(3):
        cycle_result = engine.step()
        print(cycle_result)


if __name__ == "__main__":
    main()
