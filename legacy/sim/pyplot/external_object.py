import logging

logger = logging.getLogger(__name__)

class ExternalObject:
    """Base class for external processing objects used by the simulation."""

    def __init__(self, obj_name: str) -> None:
        """
        Initialize an external object.

        Parameters
        ----------
        obj_name : str
            Name used to register the external object in the simulation manager.
        """
        self.obj_name = obj_name
        logger.info("Initializing external object %s...", self.obj_name)

    def step(self) -> None:
        """Execute one processing step."""
        return None
