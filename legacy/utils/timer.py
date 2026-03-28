import time
import logging

class Timer:
    """
    Context manager for measuring execution time of code blocks.

    Can optionally log the measured duration using a provided logger.
    """

    def __init__(self, name: str | None = None, logger: logging.Logger | None = None) -> None:
        """
        Initialize the timer.

        Parameters
        ----------
        name : str | None, optional
            Name of the timed block.
        logger : logging.Logger | None, optional
            Logger used to report execution time.
        """
        self.name = name
        self.logger = logger

        self.start: float | None = None
        self.end: float | None = None
        self.duration: float | None = None

    def __enter__(self) -> "Timer":
        """Start the timer."""
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        """Stop the timer and optionally log the duration."""
        self.end = time.perf_counter()
        self.duration = self.end - self.start

        if self.logger and self.name:
            self.logger.info(
                "Timer '%s' finished | duration=%.6f s",
                self.name,
                self.duration,
            )
