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

from manipulator_framework.examples.core.runtime._mocks import (
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
    camera = FakeCamera()
    detector = FakePersonDetector()
    tracker = FakeTracker()
    planner = FakePlanner()
    controller = FakeController()
    clock = FakeClock()

    pipeline = RuntimePipeline(
        steps=[
            SensingStep(robot=robot, camera=camera),
            EstimationStep(person_detector=detector, tracker=tracker),
            PlanningStep(planner=planner),
            ControlStep(controller=controller, dt=0.1),
            ActuationStep(robot=robot),
        ]
    )

    engine = ExecutionEngine(clock=clock, pipeline=pipeline)
    result = engine.step()

    print(result)
    print("Last robot command:", robot.last_command.to_dict() if robot.last_command else None)


if __name__ == "__main__":
    main()
