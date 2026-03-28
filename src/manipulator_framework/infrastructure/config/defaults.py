from __future__ import annotations

DEFAULT_CONFIG: dict = {
    "app": {
        "name": "manipulator_framework",
        "mode": "simulation",
    },
    "runtime": {
        "dt": 0.05,
        "max_steps": 100,
    },
    "logging": {
        "level": "INFO",
        "save_to_file": True,
    },
    "results": {
        "base_dir": "experiments/runs",
    },
    "experiment": {
        "name": "default_experiment",
        "seed": 42,
        "tags": [],
    },
}
