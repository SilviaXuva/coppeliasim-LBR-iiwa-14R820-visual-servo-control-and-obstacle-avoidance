import logging
import numpy as np

from robot import LBR_iiwa_DH
from sim.coppelia_sim.sim_object import SimObject

logger = logging.getLogger("Robot")

class Robot(LBR_iiwa_DH, SimObject):
    """CoppeliaSim interface for the KUKA LBR iiwa 14R820 manipulator."""

    def __init__(
        self,
        sim,
        should_lock_joints: bool = True,
        joint_mode: str = "dynamic",
        joint_ctrl_mode: str = "velocity",
    ) -> None:
        """
        Initialize the robot model and bind it to the CoppeliaSim robot instance.

        Parameters
        ----------
        sim : object
            CoppeliaSim simulation interface.
        should_lock_joints : bool, optional
            Whether joint velocity locks should be enabled.
        joint_mode : str, optional
            Joint mode. Supported values are: 'kinematic', 'dependent', 'dynamic'.
        joint_ctrl_mode : str, optional
            Dynamic joint control mode. Supported values are:
            'position', 'velocity', 'force'.
        """
        LBR_iiwa_DH.__init__(self)

        SimObject.__init__(
            self,
            obj_name=self.name,
            client=None,
            sim=sim,
            is_thread=False,
        )

        self.handle = self.sim.getObject(f"./{self.name}")
        self.joints_handles = self.get_joints_handles()

        if should_lock_joints:
            self.lock_joints()
        else:
            self.unlock_joints()

        self.set_joints_mode(joint_mode)
        self.set_joints_ctrl_mode(joint_ctrl_mode)
        self.set_joints_target_force(self.tau_max)

    def get_joints_handles(self) -> list[int]:
        """
        Retrieve the handles of all robot joints.

        Returns
        -------
        list[int]
            List of joint handles ordered by joint index.
        """
        joints_handles = []

        for i in range(self.n):
            joint_handle = self.sim.getObject(f"./joint{i}")
            joints_handles.append(joint_handle)

        return joints_handles

    def unlock_joints(self) -> None:
        """Disable joint velocity locking in CoppeliaSim."""
        for joint in self.joints_handles:
            self.sim.setObjectInt32Param(
                joint,
                self.sim.jointintparam_velocity_lock,
                0,
            )

    def lock_joints(self) -> None:
        """Enable joint velocity locking in CoppeliaSim."""
        for joint in self.joints_handles:
            self.sim.setObjectInt32Param(
                joint,
                self.sim.jointintparam_velocity_lock,
                1,
            )

    def set_joints_mode(self, mode: str) -> None:
        """
        Set the operating mode of all joints.

        Parameters
        ----------
        mode : str
            Joint mode. Supported values are: 'kinematic', 'dependent', 'dynamic'.
        """
        mode_map = {
            "kinematic": self.sim.jointmode_kinematic,
            "dependent": self.sim.jointmode_dependent,
            "dynamic": self.sim.jointmode_dynamic,
        }

        if mode not in mode_map:
            raise ValueError(
                f"Invalid joint mode '{mode}'. "
                f"Expected one of: {list(mode_map.keys())}."
            )

        param = mode_map[mode]

        for joint in self.joints_handles:
            self.sim.setJointMode(joint, param, 0)

    def set_joints_ctrl_mode(self, ctrl_mode: str) -> None:
        """
        Set the dynamic control mode of all joints.

        Parameters
        ----------
        ctrl_mode : str
            Dynamic control mode. Supported values are:
            'position', 'velocity', 'force'.
        """
        joint_mode = self.sim.getJointMode(self.joints_handles[0])[0]

        if joint_mode != self.sim.jointmode_dynamic:
            if joint_mode == self.sim.jointmode_kinematic:
                formatted = "kinematic"
            elif joint_mode == self.sim.jointmode_dependent:
                formatted = "dependent"
            else:
                formatted = f"unknown ({joint_mode})"

            logger.info(
                "Joint control mode was not changed because joints are set to %s mode.",
                formatted,
            )
            return

        ctrl_mode_map = {
            "position": self.sim.jointdynctrl_position,
            "velocity": self.sim.jointdynctrl_velocity,
            "force": self.sim.jointdynctrl_force,
        }

        if ctrl_mode not in ctrl_mode_map:
            raise ValueError(
                f"Invalid joint control mode '{ctrl_mode}'. "
                f"Expected one of: {list(ctrl_mode_map.keys())}."
            )

        param = ctrl_mode_map[ctrl_mode]

        for joint in self.joints_handles:
            self.sim.setObjectInt32Param(
                joint,
                self.sim.jointintparam_dynctrlmode,
                param,
            )

    def get_joints_position(self) -> np.ndarray:
        """
        Read the current joint positions from simulation.

        Returns
        -------
        np.ndarray
            Current joint position vector.
        """
        for i, joint in enumerate(self.joints_handles):
            self.q[i] = np.float64(self.sim.getJointPosition(joint))

        return self.q.copy()

    def set_joints_position(self, pos: list | np.ndarray) -> None:
        """
        Set the current joint positions directly in simulation.

        Parameters
        ----------
        pos : list | np.ndarray
            Joint position vector.
        """
        if len(pos) != self.n:
            raise ValueError(f"Expected {self.n} joint positions, got {len(pos)}.")

        for i, joint in enumerate(self.joints_handles):
            self.sim.setJointPosition(joint, np.float64(pos[i]))
            self.q[i] = np.float64(pos[i])

    def get_joints_target_position(self) -> np.ndarray:
        """
        Read the target joint positions from simulation.

        Returns
        -------
        np.ndarray
            Target joint position vector.
        """
        for i, joint in enumerate(self.joints_handles):
            self.q[i] = np.float64(self.sim.getJointTargetPosition(joint))

        return self.q.copy()

    def set_joints_target_position(self, pos: list | np.ndarray) -> None:
        """
        Set the target joint positions in simulation.

        Parameters
        ----------
        pos : list | np.ndarray
            Target joint position vector.
        """
        if len(pos) != self.n:
            raise ValueError(f"Expected {self.n} joint positions, got {len(pos)}.")

        for i, joint in enumerate(self.joints_handles):
            self.sim.setJointTargetPosition(joint, np.float64(pos[i]))
            self.q[i] = np.float64(pos[i])

    def get_joints_velocity(self) -> np.ndarray:
        """
        Read the current joint velocities from simulation.

        Returns
        -------
        np.ndarray
            Current joint velocity vector.
        """
        for i, joint in enumerate(self.joints_handles):
            self.qd[i] = np.float64(self.sim.getJointVelocity(joint))

        return self.qd.copy()

    def get_joints_target_velocity(self) -> np.ndarray:
        """
        Read the target joint velocities from simulation.

        Returns
        -------
        np.ndarray
            Target joint velocity vector.
        """
        for i, joint in enumerate(self.joints_handles):
            self.qd[i] = np.float64(self.sim.getJointTargetVelocity(joint))

        return self.qd.copy()

    def set_joints_target_velocity(self, vel: list | np.ndarray) -> None:
        """
        Set the target joint velocities in simulation.

        Parameters
        ----------
        vel : list | np.ndarray
            Target joint velocity vector.
        """
        if len(vel) != self.n:
            raise ValueError(f"Expected {self.n} joint velocities, got {len(vel)}.")

        for i, joint in enumerate(self.joints_handles):
            self.sim.setJointTargetVelocity(joint, np.float64(vel[i]))
            self.qd[i] = np.float64(vel[i])

    def get_joints_force(self) -> np.ndarray:
        """
        Read the current joint forces/torques from simulation.

        Returns
        -------
        np.ndarray
            Current joint force/torque vector.
        """
        for i, joint in enumerate(self.joints_handles):
            self.tau[i] = np.float64(self.sim.getJointForce(joint))

        return self.tau.copy()

    def get_joints_target_force(self) -> np.ndarray:
        """
        Read the target joint forces/torques from simulation.

        Returns
        -------
        np.ndarray
            Target joint force/torque vector.
        """
        for i, joint in enumerate(self.joints_handles):
            self.tau[i] = np.float64(self.sim.getJointTargetForce(joint))

        return self.tau.copy()

    def set_joints_target_force(self, tau: list | np.ndarray) -> None:
        """
        Set the target joint forces/torques in simulation.

        Parameters
        ----------
        tau : list | np.ndarray
            Target joint force/torque vector.
        """
        if len(tau) != self.n:
            raise ValueError(f"Expected {self.n} joint torques, got {len(tau)}.")

        for i, joint in enumerate(self.joints_handles):
            self.sim.setJointTargetForce(joint, np.float64(tau[i]))
            self.tau[i] = np.float64(tau[i])

    def step(self) -> None:
        """Update the cached joint position vector from simulation."""
        self.get_joints_position()
