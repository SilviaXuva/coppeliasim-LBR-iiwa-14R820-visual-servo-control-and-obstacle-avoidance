from __future__ import annotations

from manipulator_framework.application.composition.simulation_composer import SimulationComposer


class FakeSimClient:
    pass


def main() -> None:
    composer = SimulationComposer(sim_client=FakeSimClient())

    robot = composer.build_coppeliasim_robot(
        robot_handle="iiwa_handle",
        joint_names=tuple(f"joint_{i+1}" for i in range(7)),
    )
    simulator = composer.build_coppeliasim_simulator()

    print("Simulation adapter composed successfully.")
    print(robot)
    print(simulator)


if __name__ == "__main__":
    main()
