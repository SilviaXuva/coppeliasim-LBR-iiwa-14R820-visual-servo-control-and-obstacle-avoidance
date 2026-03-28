import math

from sim.coppelia_sim.sim_object import SimObject

class Conveyor(SimObject):
    """Interface for controlling a conveyor belt in CoppeliaSim."""

    path = "./conveyor"  # CoppeliaSim object path/name
    tol = 1e-4           # Velocity tolerance to consider the conveyor stopped

    def __init__(self, sim, vel: float) -> None:
        """
        Initialize the conveyor object and start it with a given velocity.

        Parameters
        ----------
        sim : object
            CoppeliaSim remote API or simulation interface.
        vel : float
            Initial conveyor velocity.
        """
        super().__init__(
            obj_name="Conveyor",
            client=None,
            sim=sim,
            is_thread=False,
        )

        self.handle = self.sim.getObjectHandle(self.path)
        self.move(vel)

    def move(self, vel: float) -> None:
        """
        Set the conveyor velocity.

        Parameters
        ----------
        vel : float
            Desired conveyor velocity.
        """
        self.sim.writeCustomTableData(
            self.handle,
            "__ctrl__",
            {"vel": vel},
        )

    def get_velocity(self) -> float:
        """
        Get the current conveyor velocity.

        Returns
        -------
        float
            Current velocity read from simulation state.
        """
        state = self.sim.readCustomTableData(self.handle, "__state__")
        return state["vel"]

    def is_stopped(self) -> bool:
        """
        Check whether the conveyor is stopped within a tolerance.

        Returns
        -------
        bool
            True if velocity is approximately zero, False otherwise.
        """
        vel = self.get_velocity()
        return math.isclose(vel, 0.0, abs_tol=self.tol)
