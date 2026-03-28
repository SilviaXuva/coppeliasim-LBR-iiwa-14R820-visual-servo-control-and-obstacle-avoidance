import numpy as np

from sim import CoppeliaSim, Robot, PyPlot
from utils import DEG_TO_RAD, Experiment, Timer

class RobotTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "1.LBR_iiwa.ttt",
            "duration": 10.0,
            "robot_target_vel": [0, 0, 0, 0, 0, 0, 90 * DEG_TO_RAD],
        }

        super().__init__(
            test_id=3,
            name="robot_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            if self.config['scene'] is None:
                psim = PyPlot()
                psim.start()

                try:
                    while psim.get_sim_time() < self.config['duration']:
                        psim.step()
                finally:
                    psim.stop()

            else:
                csim = CoppeliaSim(
                    stepping=False,
                    scene=self.config["scene"],
                )

                robot = Robot(csim.sim)
                csim.add_object(robot)

                target_vel = np.asarray(self.config["robot_target_vel"], dtype=float)

                csim.start()

                try:
                    while csim.sim.getSimulationTime() < self.config["duration"]:
                        robot.set_joints_target_velocity(target_vel)
                        csim.step()
                finally:
                    csim.stop()

        self.save_results({
            "duration": float(t.duration),
        })
