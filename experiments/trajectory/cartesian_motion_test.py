from __future__ import annotations

import numpy as np
from spatialmath import SE3

from sim import CoppeliaSim, Robot, TrajDrawing
from control.trajectory import CartesianTrajectory
from utils import Experiment, Timer


class CartesianMotionTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "1.LBR_iiwa.ttt",
            "duration": 8.0,
            "trajectory_duration": 5.0,
            "profile": "cubic",
            "target_offset": [1, 0.0, 0],
        }

        super().__init__(
            test_id=3,
            name="cartesian_motion_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        time_history: list[float] = []
        x_ref_history: list[list[float]] = []
        dx_ref_history: list[list[float]] = []
        ddx_ref_history: list[list[float]] = []
        q_ref_history: list[list[float]] = []

        with Timer("simulation", self.logger) as t:
            csim = CoppeliaSim(
                stepping=True,
                scene=self.config["scene"],
            )

            robot = Robot(
                csim.sim,
                joint_ctrl_mode="position",
            )
            csim.add_object(robot)

            traj_drawing = TrajDrawing(csim.sim)
            csim.add_object(traj_drawing)

            csim.start()

            try:
                q_start = np.asarray(robot.get_joints_position(), dtype=float)
                T_start = robot.fkine(q_start)

                dx, dy, dz = self.config["target_offset"]
                T_goal = T_start * SE3.Trans(dx, dy, dz)

                traj = CartesianTrajectory(
                    T_start=T_start,
                    T_goal=T_goal,
                    duration=float(self.config["trajectory_duration"]),
                    profile=self.config["profile"],
                )

                q_seed = q_start.copy()

                while csim.sim.getSimulationTime() < self.config["duration"]:
                    sim_time = float(csim.sim.getSimulationTime())
                    sample = traj.sample(sim_time)

                    ik_sol = robot.ets().ik_LM(
                        sample.T,
                        q0=q_seed,
                        ilimit=30,
                        slimit=200,
                        tol=1e-3,
                        mask=np.ones(6),
                        k=1e-4,
                        joint_limits=True,
                        method="sugihara",
                    )
                    print(ik_sol)
                    q_ref = ik_sol[0]

                    q_ref = np.asarray(q_ref, dtype=float)

                    robot.set_joints_target_position(q_ref.tolist())
                    traj_drawing.ref_pos = sample.T.t

                    q_seed = robot.get_joints_position()

                    time_history.append(sim_time)
                    x_ref_history.append(sample.x.tolist())
                    dx_ref_history.append(sample.dx.tolist())
                    ddx_ref_history.append(sample.ddx.tolist())
                    q_ref_history.append(q_ref.tolist())

                    csim.step()

            finally:
                csim.stop()

        self.save_results(
            {
                "duration": float(t.duration),
                "trajectory_duration": float(self.config["trajectory_duration"]),
                "profile": self.config["profile"],
                "q_start": q_start.tolist(),
                "T_start": T_start.A.tolist(),
                "T_goal": T_goal.A.tolist(),
                "time": time_history,
                "x_ref": x_ref_history,
                "dx_ref": dx_ref_history,
                "ddx_ref": ddx_ref_history,
                "q_ref": q_ref_history,
            }
        )
        self.teardown()
