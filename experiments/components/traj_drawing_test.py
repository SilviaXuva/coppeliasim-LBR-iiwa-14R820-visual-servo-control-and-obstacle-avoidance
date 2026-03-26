import numpy as np

from sim import CoppeliaSim, Robot, TrajDrawing
from utils import DEG_TO_RAD, Experiment, Timer

class TrajDrawingTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "4.Vision-based.ttt",
            "duration": 10.0,
            "robot_target_vel": [90 * DEG_TO_RAD, 0, 0, 0, 0, 0, 90 * DEG_TO_RAD],
        }

        super().__init__(
            test_id=6,
            name="traj_drawing_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            csim = CoppeliaSim(
                stepping=False,
                scene=self.config["scene"],
            )

            robot = Robot(csim.sim)
            traj_drawing = TrajDrawing(csim.sim)

            csim.add_object(robot)
            csim.add_object(traj_drawing)

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
