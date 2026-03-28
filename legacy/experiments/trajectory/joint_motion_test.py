from __future__ import annotations

import numpy as np

from sim import CoppeliaSim, Robot, TrajDrawing
from robot.lbr_iiwa import LBR_iiwa_DH
from control.trajectory import JointTrajectory
from utils import Experiment, Timer

class JointMotionTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "1.LBR_iiwa.ttt",
            "duration": 8.0,
            "trajectory_duration": 5.0,
            "profile": "quintic"
        }

        super().__init__(
            test_id=2,
            name="joint_motion_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            if self.config["scene"] is None:
                robot = LBR_iiwa_DH()

                q_start = np.asarray(robot.get_joints_position(), dtype=float)
                q_goal = np.asarray(robot.qz, dtype=float)

                traj = JointTrajectory(
                    q_start=q_start,
                    q_goal=q_goal,
                    duration=self.config["trajectory_duration"],
                    profile=self.config["profile"],
                )

                while csim.sim.getSimulationTime() < self.config["duration"]:
                    sim_time = float(csim.sim.getSimulationTime())
                    sample = traj.sample(sim_time)

                    robot.set_joints_target_position(sample.q.tolist())
                    traj_drawing.ref_pos = robot.fkine(sample.q.tolist()).t

                    csim.step()

            else:
                csim = CoppeliaSim(
                    stepping=True,
                    scene=self.config["scene"]
                )

                robot = Robot(
                    csim.sim,
                    joint_ctrl_mode='position'
                )
                csim.add_object(robot)

                traj_drawing = TrajDrawing(csim.sim)
                csim.add_object(traj_drawing)

                csim.start()

                try:
                    q_start = np.asarray(robot.get_joints_position(), dtype=float)
                    q_goal = np.asarray(robot.qz, dtype=float)

                    traj = JointTrajectory(
                        q_start=q_start,
                        q_goal=q_goal,
                        duration=self.config["trajectory_duration"],
                        profile=self.config["profile"],
                    )

                    while csim.sim.getSimulationTime() < self.config["duration"]:
                        sim_time = float(csim.sim.getSimulationTime())
                        sample = traj.sample(sim_time)

                        robot.set_joints_target_position(sample.q.tolist())
                        traj_drawing.ref_pos = robot.fkine(sample.q.tolist()).t

                        csim.step()

                finally:
                    csim.stop()

        self.save_results(
            {
                "duration": float(t.duration),
                "trajectory_duration": float(self.config["trajectory_duration"]),
                "profile": self.config["profile"],
                "q0": robot.qr,
                "q1": robot.qz
            }
        )
        self.teardown()
