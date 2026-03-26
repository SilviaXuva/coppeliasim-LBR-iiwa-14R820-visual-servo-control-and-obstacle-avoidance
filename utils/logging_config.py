from datetime import datetime
import logging
from pathlib import Path

# Global variables used to keep the current execution state
_RUN_ROOT: Path | None = None
_EXP_COUNTER: int = 0

# Global context of the current experiment
_CURRENT_EXP_ID: str | int = "-"
_CURRENT_EXP_NAME: str = "-"

def set_experiment_context(exp_id: int | str, exp_name: str) -> None:
    """Set the current experiment context used by log records."""
    global _CURRENT_EXP_ID, _CURRENT_EXP_NAME
    _CURRENT_EXP_ID = exp_id
    _CURRENT_EXP_NAME = exp_name

def clear_experiment_context() -> None:
    """Clear the current experiment context and restore default values."""
    global _CURRENT_EXP_ID, _CURRENT_EXP_NAME
    _CURRENT_EXP_ID = "-"
    _CURRENT_EXP_NAME = "-"

class ExperimentContextFilter(logging.Filter):
    """
    Ensure every log record contains exp_id and exp_name.

    If a record already defines exp_id/exp_name (for example via LoggerAdapter),
    those values are preserved. Otherwise, the current global experiment context
    is applied.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "exp_id"):
            record.exp_id = _CURRENT_EXP_ID
        if not hasattr(record, "exp_name"):
            record.exp_name = _CURRENT_EXP_NAME
        return True

def _create_run_root() -> Path:
    """Create the root directory for the current execution and configure logging."""
    global _RUN_ROOT

    if _RUN_ROOT is not None:
        return _RUN_ROOT

    base_dir = Path("outputs")
    now = datetime.now()

    month_num = now.strftime("%m")
    month_name = now.strftime("%b").lower()
    month_dir = base_dir / f"{month_num}-{month_name}"
    day_dir = month_dir / f"{now.day:02d}"
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    run_root = day_dir / timestamp
    run_root.mkdir(parents=True, exist_ok=True)

    log_path = run_root / "execution.log"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | [%(exp_id)s:%(exp_name)s] | %(name)s | "
            "%(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    context_filter = ExperimentContextFilter()

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(context_filter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        logger.addHandler(file_handler)

        logger.addFilter(context_filter)

    context_config = {
        "CoppeliaSim": logging.INFO,
        "Robot": logging.DEBUG,
        "Vision Sensor": logging.DEBUG,
        "Gripper": logging.DEBUG,
        "Trajectory Drawing": logging.DEBUG,
        "Experiment": logging.DEBUG,
    }
    for name, level in context_config.items():
        logging.getLogger(name).setLevel(level)

    logger.info("Logging initialized in '%s'", log_path)

    _RUN_ROOT = run_root
    return run_root

def setup_logging(test_id: int, name: str) -> Path:
    """
    Create the execution root directory if needed and the subdirectory
    corresponding to the current experiment.

    Parameters
    ----------
    test_id : int
        Experiment identifier.
    name : str
        Experiment name.

    Returns
    -------
    Path
        Path to the experiment run directory.
    """
    global _EXP_COUNTER

    run_root = _create_run_root()

    _EXP_COUNTER += 1
    experiment_dir_name = f"{_EXP_COUNTER:02d}_{test_id:02d}_{name}"
    run_dir = run_root / experiment_dir_name
    run_dir.mkdir(exist_ok=True)

    return run_dir
