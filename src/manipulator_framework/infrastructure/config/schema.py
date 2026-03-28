from __future__ import annotations

from typing import Any


class ConfigurationValidationError(ValueError):
    """Raised when configuration content violates the expected schema."""


def validate_config_dict(config: dict[str, Any]) -> None:
    required_sections = {"app", "runtime", "logging", "results", "experiment"}
    missing_sections = required_sections.difference(config.keys())
    if missing_sections:
        raise ConfigurationValidationError(
            f"Missing required config sections: {sorted(missing_sections)}"
        )

    if not isinstance(config["app"].get("name"), str):
        raise ConfigurationValidationError("'app.name' must be a string.")

    if config["app"].get("mode") not in {"simulation", "experiment", "benchmark", "ros2"}:
        raise ConfigurationValidationError(
            "'app.mode' must be one of: simulation, experiment, benchmark, ros2."
        )

    if not isinstance(config["runtime"].get("dt"), (int, float)):
        raise ConfigurationValidationError("'runtime.dt' must be numeric.")

    if config["runtime"]["dt"] <= 0.0:
        raise ConfigurationValidationError("'runtime.dt' must be positive.")

    if not isinstance(config["runtime"].get("max_steps"), int):
        raise ConfigurationValidationError("'runtime.max_steps' must be an integer.")

    if config["runtime"]["max_steps"] <= 0:
        raise ConfigurationValidationError("'runtime.max_steps' must be positive.")

    if not isinstance(config["experiment"].get("seed"), int):
        raise ConfigurationValidationError("'experiment.seed' must be an integer.")

    if not isinstance(config["results"].get("base_dir"), str):
        raise ConfigurationValidationError("'results.base_dir' must be a string.")
