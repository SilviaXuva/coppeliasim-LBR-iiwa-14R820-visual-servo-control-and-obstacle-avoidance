import logging
from threading import Event, Thread

logger = logging.getLogger("PyPlot")

class SimObject(Thread):
    """Base class for objects associated with a CoppeliaSim simulation."""

    def __init__(
        self,
        obj_name: str,
        is_thread: bool = False,
    ) -> None:
        """
        Initialize a simulation object.

        Parameters
        ----------
        obj_name : str
            Name used to register the object in the simulation manager.
        is_thread : bool, optional
            Whether the object should run as a background thread.
        """
        self.obj_name = obj_name
        self.is_thread = is_thread

        logger.info("Initializing CoppeliaSim object %s...", self.obj_name)

        if self.is_thread:
            super().__init__(daemon=True)
            self.event = Event()

    def step(self) -> None:
        """Execute one simulation update step."""
        return None
