import numpy as np
import time

from sim import CoppeliaSim, Robot
from robot.lbr_iiwa import LBR_iiwa_DH
from utils import Experiment, Timer

class InverseKinematicsTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "1.LBR_iiwa.ttt",
            "q0": None,
            "ilimit": 30,
            "slimit": 200,
            "tol": 1e-3,
            "mask": np.ones(6),
            "k": 0.0001,
            "joint_limits": False,
            "method": 'sugihara'
        }

        super().__init__(
            test_id=1,
            name="inverse_kinematics_test",
            config=config or default_config,
        )

    def run(self):
        result = {}

        if self.config["scene"] is None:
            robot = LBR_iiwa_DH()
        
        else:
            csim = CoppeliaSim(
                stepping=False,
                scene=self.config["scene"]
            )
            robot = Robot(csim.sim)
            csim.add_object(robot)

        T0 = robot.fkine(robot.qz)
        T1 = robot.fkine(robot.qr)
        result['T0'] = T0
        result['T1'] = T1

        with Timer('IKINE - T0', self.logger) as t0:
            ik_sol0 = robot.ets().ik_LM(
                T0,
                q0=self.config['q0'],
                ilimit=self.config['ilimit'],
                slimit=self.config['slimit'],
                tol=self.config['tol'],
                mask=self.config['mask'],
                k=self.config['k'],
                joint_limits=self.config['joint_limits'],
                method=self.config['method'],
            )
            result['ik_sol0'] = ik_sol0
        result['duration0'] = t0.duration

        with Timer('IKINE - T1', self.logger) as t1:
            ik_sol1 = robot.ets().ik_LM(
                T1,
                q0=self.config['q0'],
                ilimit=self.config['ilimit'],
                slimit=self.config['slimit'],
                tol=self.config['tol'],
                mask=self.config['mask'],
                k=self.config['k'],
                joint_limits=self.config['joint_limits'],
                method=self.config['method'],
            )
            result['ik_sol1'] = ik_sol1
        result['duration1'] = t1.duration

        if self.config["scene"] is None:
            robot.plot(ik_sol0[0], block=False)
            time.sleep(5)
            robot.plot(ik_sol1[0], block=False)
            time.sleep(5)
        else:
            robot.set_joints_position(ik_sol0[0])
            time.sleep(5)
            robot.set_joints_position(ik_sol1[0])
            time.sleep(5)
        
        self.save_results(result)
        self.teardown()
