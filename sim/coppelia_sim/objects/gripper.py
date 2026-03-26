import logging
import math

from sim.coppelia_sim.sim_object import SimObject

logger = logging.getLogger("Gripper")

class Robotiq2F85(SimObject):
    """Interface for the Robotiq 2F-85 gripper in CoppeliaSim."""

    class Actuation:
        """Actuation timing and joint velocity settings."""

        t_tot = 1.0  # Total actuation time [s]

        class ClosePhase1:
            vel_left = -0.08
            vel_right = -0.08

        class ClosePhase2:
            vel_left = -0.08
            vel_right = -0.08

        class OpenPhase1:
            vel_left = 0.08
            vel_right = 0.08

        class OpenPhase2:
            vel_left = 0.08
            vel_right = 0.08

    class JointsOpenedTol:
        """Tolerance used to determine whether the gripper is open."""

        left = 1e-3
        right = 1e-3

    class Proximity:
        """Tolerance used in proximity checking."""

        tol = 1e-3

    def __init__(self, client, sim) -> None:
        """
        Initialize the Robotiq 2F-85 gripper.

        Parameters
        ----------
        client : object
            ZMQ or remote API client used to require simulation modules.
        sim : object
            CoppeliaSim simulation interface.
        """
        super().__init__(
            obj_name="Robotiq2F85",
            client=client,
            sim=sim,
            is_thread=False,
        )

        self.simIK = self.client.require("simIK")

        self.joint_left = self.sim.getObject("./active1")
        self.joint_left_opened = self.sim.getJointPosition(self.joint_left)

        self.joint_right = self.sim.getObject("./active2")
        self.joint_right_opened = self.sim.getJointPosition(self.joint_right)

        self.base = self.sim.getObject("./ROBOTIQ85")
        self.tip_left = self.sim.getObject("./LclosureDummyA")
        self.target_left = self.sim.getObject("./LclosureDummyB")
        self.tip_right = self.sim.getObject("./RclosureDummyA")
        self.target_right = self.sim.getObject("./RclosureDummyB")

        self.connector = self.sim.getObject("./attachPoint")
        self.prox_sensor = self.sim.getObject("./attachProxSensor")

        self.move = False
        self.close_cmd = False
        self.start = None
        self.end = None

        self.create_ik_env()

    def create_ik_env(self) -> None:
        """Create the IK environment used to synchronize the gripper fingers."""
        self.ik_env = self.simIK.createEnvironment()

        self.ik_group_left = self.simIK.createGroup(self.ik_env)
        self.simIK.addElementFromScene(
            self.ik_env,
            self.ik_group_left,
            self.base,
            self.tip_left,
            self.target_left,
            self.simIK.constraint_x + self.simIK.constraint_z,
        )

        self.ik_group_right = self.simIK.createGroup(self.ik_env)
        self.simIK.addElementFromScene(
            self.ik_env,
            self.ik_group_right,
            self.base,
            self.tip_right,
            self.target_right,
            self.simIK.constraint_x + self.simIK.constraint_z,
        )

    def is_open(self) -> bool:
        """
        Check whether both gripper joints are at their opened positions.

        Returns
        -------
        bool
            True if the gripper is open, False otherwise.
        """
        joint_left_pos = self.sim.getJointPosition(self.joint_left)
        is_jleft_opened = math.isclose(
            joint_left_pos,
            self.joint_left_opened,
            abs_tol=self.JointsOpenedTol.left,
        )

        joint_right_pos = self.sim.getJointPosition(self.joint_right)
        is_jright_opened = math.isclose(
            joint_right_pos,
            self.joint_right_opened,
            abs_tol=self.JointsOpenedTol.right,
        )

        return is_jleft_opened and is_jright_opened

    def open(self) -> None:
        """Start the gripper opening motion."""
        self.move = True
        self.close_cmd = False
        self.start = None
        self.end = None

    def close(self) -> None:
        """Start the gripper closing motion."""
        self.move = True
        self.close_cmd = True
        self.start = None
        self.end = None

    def stop_motion(self) -> None:
        """Stop gripper motion and set joint target velocities to zero."""
        self.move = False
        self.start = None
        self.end = None
        self.sim.setJointTargetVelocity(self.joint_left, 0.0)
        self.sim.setJointTargetVelocity(self.joint_right, 0.0)

    def step(self) -> None:
        """Advance one simulation step of the current gripper motion command."""
        current_time = self.sim.getSimulationTime()

        if self.move:
            if self.start is None:
                self.start = current_time
                self.end = self.start + self.Actuation.t_tot

            if current_time < self.end:
                self._actuate(self.close_cmd)
            else:
                self.stop_motion()
        else:
            self.sim.setJointTargetVelocity(self.joint_left, 0.0)
            self.sim.setJointTargetVelocity(self.joint_right, 0.0)

        self.apply_ik()

    def _actuate(self, close: bool) -> None:
        """
        Apply joint velocities for the opening or closing motion.

        Parameters
        ----------
        close : bool
            If True, close the gripper. Otherwise, open it.
        """
        p_left = self.sim.getJointPosition(self.joint_left)
        p_right = self.sim.getJointPosition(self.joint_right)

        if close:
            if p_left < p_right - 0.008:
                self.sim.setJointTargetVelocity(
                    self.joint_left,
                    self.Actuation.ClosePhase1.vel_left,
                )
                self.sim.setJointTargetVelocity(
                    self.joint_right,
                    self.Actuation.ClosePhase1.vel_right,
                )
            else:
                self.sim.setJointTargetVelocity(
                    self.joint_left,
                    self.Actuation.ClosePhase2.vel_left,
                )
                self.sim.setJointTargetVelocity(
                    self.joint_right,
                    self.Actuation.ClosePhase2.vel_right,
                )
        else:
            if p_left < p_right:
                self.sim.setJointTargetVelocity(
                    self.joint_left,
                    self.Actuation.OpenPhase1.vel_left,
                )
                self.sim.setJointTargetVelocity(
                    self.joint_right,
                    self.Actuation.OpenPhase1.vel_right,
                )
            else:
                self.sim.setJointTargetVelocity(
                    self.joint_left,
                    self.Actuation.OpenPhase2.vel_left,
                )
                self.sim.setJointTargetVelocity(
                    self.joint_right,
                    self.Actuation.OpenPhase2.vel_right,
                )

    def apply_ik(self) -> None:
        """Apply IK updates for both gripper fingers."""
        self.simIK.handleGroup(
            self.ik_env,
            self.ik_group_left,
            {"syncWorlds": True},
        )
        self.simIK.handleGroup(
            self.ik_env,
            self.ik_group_right,
            {"syncWorlds": True},
        )

    def is_object_detected(self, shape_handle: int) -> tuple[bool, tuple]:
        """
        Check whether a shape is detected near the gripper.

        Parameters
        ----------
        shape_handle : int
            Handle of the shape to be checked.

        Returns
        -------
        tuple[bool, tuple]
            A tuple containing:
            - True if the object is detected within the proximity tolerance.
            - The raw proximity sensor return tuple.
        """
        prox = self.sim.checkProximitySensor(self.prox_sensor, shape_handle)
        is_detected = prox[0] == 1
        is_nearby = math.isclose(prox[1], 0.0, abs_tol=self.Proximity.tol)

        return is_detected and is_nearby, prox

    def can_attach(self, shape_handle: int) -> bool:
        """
        Check whether the object can be attached to the gripper.

        Parameters
        ----------
        shape_handle : int
            Handle of the shape to be checked.

        Returns
        -------
        bool
            True if the object is detected nearby and the gripper is open.
        """
        detected, _ = self.is_object_detected(shape_handle)
        return detected and self.is_open()

    def attach(self, shape_handle: int) -> bool:
        """
        Attach a shape to the gripper connector.

        Parameters
        ----------
        shape_handle : int
            Handle of the shape to be attached.

        Returns
        -------
        bool
            True if the attachment succeeded, False otherwise.
        """
        if not self.can_attach(shape_handle):
            return False

        ret = self.sim.setObjectParent(shape_handle, self.connector, True) == 1
        if ret:
            logger.debug("Shape %s attached to gripper.", shape_handle)
        return ret

    def detach(self, shape_handle: int) -> bool:
        """
        Detach a shape from the gripper.

        Parameters
        ----------
        shape_handle : int
            Handle of the shape to be detached.

        Returns
        -------
        bool
            True if the detachment succeeded, False otherwise.
        """
        ret = self.sim.setObjectParent(shape_handle, -1, True) == 1
        if ret:
            logger.debug("Shape %s detached from gripper.", shape_handle)
        return ret

    def attach_by_path(self, shape_path: str) -> bool:
        """
        Attach a shape to the gripper using its CoppeliaSim path.

        Parameters
        ----------
        shape_path : str
            Path of the shape in CoppeliaSim.

        Returns
        -------
        bool
            True if the attachment succeeded, False otherwise.
        """
        shape_handle = self.sim.getObject(shape_path)
        return self.attach(shape_handle)

    def detach_by_path(self, shape_path: str) -> bool:
        """
        Detach a shape from the gripper using its CoppeliaSim path.

        Parameters
        ----------
        shape_path : str
            Path of the shape in CoppeliaSim.

        Returns
        -------
        bool
            True if the detachment succeeded, False otherwise.
        """
        shape_handle = self.sim.getObject(shape_path)
        return self.detach(shape_handle)

    def stop(self) -> None:
        """Release resources associated with the IK environment."""
        self.stop_motion()
        self.simIK.eraseEnvironment(self.ik_env)
