import json
import logging
from pathlib import Path

from utils.formatter import serialize
from utils.logging_config import (
    clear_experiment_context,
    set_experiment_context,
    setup_logging,
)

class Experiment:
    """Base class for structured experiment execution."""

    def __init__(self, test_id: int, name: str, config: dict | None = None) -> None:
        """
        Initialize an experiment.

        Parameters
        ----------
        test_id : int
            Experiment identifier.
        name : str
            Experiment name.
        config : dict | None, optional
            Experiment configuration dictionary.
        """
        self.test_id = test_id
        self.name = name
        self.config = config or {}

        self.run_dir: Path | None = None
        self.logger = logging.getLogger("Experiment")

        self.setup()
        
    def setup(self) -> None:
        """Create the run directory, initialize logging, and save the configuration."""
        self.run_dir = setup_logging(self.test_id, self.name)

        self.logger.info(
            "=== Starting experiment %s (id=%s) ===",
            self.name,
            self.test_id,
        )
        self.logger.info("Run directory: %s", self.run_dir)

        config_path = self.run_dir / "config.json"
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, default=serialize, ensure_ascii=False)

        self.logger.info("Configuration saved to %s", config_path)

    def run(self) -> None:
        """
        Execute the experiment lifecycle.

        This template method sets the experiment context, optionally builds
        resources, runs the main experiment logic, and performs teardown.
        """
        set_experiment_context(self.test_id, self.name)
        try:
            self.build()
            self._run()
        finally:
            self.teardown()
            clear_experiment_context()

    def _run(self) -> None:
        """Implement the main experiment logic in subclasses."""
        raise NotImplementedError

    def save_results(self, results: dict) -> None:
        """
        Save experiment results as a JSON file inside the run directory.

        Parameters
        ----------
        results : dict
            Results dictionary to be serialized.
        """
        if self.run_dir is None:
            raise RuntimeError("Experiment not initialized.")

        path = self.run_dir / "results.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, default=serialize, ensure_ascii=False)

        self.logger.info("Results saved to %s", path)

    def build(self) -> None:
        """Optional initialization step to be overridden by subclasses."""
        return None

    def teardown(self) -> None:
        """Finalize the experiment execution."""
        self.logger.info(
            "=== Finished experiment %s (id=%s) ===",
            self.name,
            self.test_id,
        )
