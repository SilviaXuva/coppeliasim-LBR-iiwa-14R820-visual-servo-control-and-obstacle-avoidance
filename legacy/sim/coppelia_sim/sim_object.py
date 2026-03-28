import logging
from threading import Event, Thread

from coppeliasim_zmqremoteapi_client import RemoteAPIClient

logger = logging.getLogger("CoppeliaSim")

class SimObject(Thread):
    """Base class for objects associated with a CoppeliaSim simulation."""

    def __init__(
        self,
        obj_name: str,
        client=None,
        sim=None,
        is_thread: bool = False,
    ) -> None:
        """
        Initialize a simulation object.

        Parameters
        ----------
        obj_name : str
            Name used to register the object in the simulation manager.
        client : object | None, optional
            Existing RemoteAPI client.
        sim : object | None, optional
            Existing CoppeliaSim simulation interface.
        is_thread : bool, optional
            Whether the object should run as a background thread.
        """
        self.obj_name = obj_name
        self.client = client
        self.sim = sim
        self.is_thread = is_thread

        logger.info("Initializing CoppeliaSim object %s...", self.obj_name)

        if self.is_thread:
            super().__init__(daemon=True)
            self.event = Event()

            self.client = RemoteAPIClient()
            self.sim = self.client.require("sim")

    def step(self) -> None:
        """Execute one simulation update step."""
        return None
