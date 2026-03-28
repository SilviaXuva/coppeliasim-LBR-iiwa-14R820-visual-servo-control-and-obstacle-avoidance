from __future__ import annotations

import pytest

from manipulator_framework.infrastructure.config.schema import (
    ConfigurationValidationError,
    validate_config_dict,
)


def test_validate_config_dict_accepts_valid_config() -> None:
    config = {
        "app": {"name": "framework", "mode": "simulation"},
        "runtime": {"dt": 0.01, "max_steps": 100},
        "logging": {"level": "INFO", "save_to_file": True},
        "results": {"base_dir": "experiments/runs"},
        "experiment": {"name": "demo", "seed": 42, "tags": []},
    }

    validate_config_dict(config)


def test_validate_config_dict_rejects_missing_section() -> None:
    config = {
        "app": {"name": "framework", "mode": "simulation"},
        "runtime": {"dt": 0.01, "max_steps": 100},
        "logging": {"level": "INFO", "save_to_file": True},
        "results": {"base_dir": "experiments/runs"},
    }

    with pytest.raises(ConfigurationValidationError, match="Missing required config sections"):
        validate_config_dict(config)


def test_validate_config_dict_rejects_invalid_dt() -> None:
    config = {
        "app": {"name": "framework", "mode": "simulation"},
        "runtime": {"dt": -0.01, "max_steps": 100},
        "logging": {"level": "INFO", "save_to_file": True},
        "results": {"base_dir": "experiments/runs"},
        "experiment": {"name": "demo", "seed": 42, "tags": []},
    }

    with pytest.raises(ConfigurationValidationError, match="'runtime.dt' must be positive."):
        validate_config_dict(config)
