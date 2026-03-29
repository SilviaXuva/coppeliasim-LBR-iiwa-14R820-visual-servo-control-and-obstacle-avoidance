from __future__ import annotations

from typing import Any


class ConfigurationValidationError(ValueError):
    """Raised when configuration content violates the expected schema."""


def _require_section(config: dict[str, Any], section: str) -> dict[str, Any]:
    value = config.get(section)
    if not isinstance(value, dict):
        raise ConfigurationValidationError(f"'{section}' section must be a mapping.")
    return value


def _require_string(section: dict[str, Any], key: str, fq_name: str) -> str:
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationValidationError(f"'{fq_name}' must be a non-empty string.")
    return value


def _require_bool(section: dict[str, Any], key: str, fq_name: str) -> bool:
    value = section.get(key)
    if not isinstance(value, bool):
        raise ConfigurationValidationError(f"'{fq_name}' must be a boolean.")
    return value


def _require_number(section: dict[str, Any], key: str, fq_name: str) -> float:
    value = section.get(key)
    if not isinstance(value, (int, float)):
        raise ConfigurationValidationError(f"'{fq_name}' must be numeric.")
    return float(value)


def _require_positive_number(section: dict[str, Any], key: str, fq_name: str) -> float:
    value = _require_number(section, key, fq_name)
    if value <= 0.0:
        raise ConfigurationValidationError(f"'{fq_name}' must be positive.")
    return value


def _require_positive_int(section: dict[str, Any], key: str, fq_name: str) -> int:
    value = section.get(key)
    if not isinstance(value, int):
        raise ConfigurationValidationError(f"'{fq_name}' must be an integer.")
    if value <= 0:
        raise ConfigurationValidationError(f"'{fq_name}' must be positive.")
    return value


def validate_config_dict(config: dict[str, Any]) -> None:
    required_sections = {
        "app",
        "runtime",
        "logging",
        "results",
        "experiment",
        "scenario",
        "controller",
        "planning",
        "visual_servoing",
        "perception",
        "obstacle_avoidance",
    }
    missing_sections = required_sections.difference(config.keys())
    if missing_sections:
        raise ConfigurationValidationError(
            f"Missing required config sections: {sorted(missing_sections)}"
        )

    app = _require_section(config, "app")
    runtime = _require_section(config, "runtime")
    logging = _require_section(config, "logging")
    results = _require_section(config, "results")
    experiment = _require_section(config, "experiment")
    scenario = _require_section(config, "scenario")
    controller = _require_section(config, "controller")
    planning = _require_section(config, "planning")
    visual_servoing = _require_section(config, "visual_servoing")
    perception = _require_section(config, "perception")
    obstacle_avoidance = _require_section(config, "obstacle_avoidance")

    _require_string(app, "name", "app.name")
    if app.get("mode") not in {"simulation", "experiment", "benchmark", "ros2"}:
        raise ConfigurationValidationError(
            "'app.mode' must be one of: simulation, experiment, benchmark, ros2."
        )
    _require_string(app, "use_case", "app.use_case")

    _require_positive_number(runtime, "dt", "runtime.dt")
    _require_positive_int(runtime, "max_steps", "runtime.max_steps")
    _require_bool(runtime, "save_runtime_series", "runtime.save_runtime_series")

    _require_string(logging, "level", "logging.level")
    _require_bool(logging, "save_to_file", "logging.save_to_file")

    _require_string(results, "base_dir", "results.base_dir")

    _require_string(experiment, "name", "experiment.name")
    if not isinstance(experiment.get("seed"), int):
        raise ConfigurationValidationError("'experiment.seed' must be an integer.")
    if not isinstance(experiment.get("tags"), list):
        raise ConfigurationValidationError("'experiment.tags' must be a list.")
    if not isinstance(experiment.get("notes"), str):
        raise ConfigurationValidationError("'experiment.notes' must be a string.")

    _require_string(scenario, "name", "scenario.name")

    _require_string(controller, "kind", "controller.kind")
    gains = _require_section(controller, "gains")
    _require_number(gains, "kp", "controller.gains.kp")
    _require_number(gains, "kd", "controller.gains.kd")
    _require_number(gains, "ki", "controller.gains.ki")

    limits = _require_section(controller, "limits")
    _require_positive_number(limits, "max_velocity", "controller.limits.max_velocity")
    _require_positive_number(limits, "max_acceleration", "controller.limits.max_acceleration")

    _require_string(planning, "kind", "planning.kind")
    _require_positive_number(planning, "duration", "planning.duration")

    _require_bool(visual_servoing, "enabled", "visual_servoing.enabled")
    _require_string(visual_servoing, "kind", "visual_servoing.kind")
    _require_string(visual_servoing, "target_frame", "visual_servoing.target_frame")
    _require_string(visual_servoing, "camera_frame", "visual_servoing.camera_frame")
    _require_positive_number(visual_servoing, "gain", "visual_servoing.gain")

    person_detector = _require_section(perception, "person_detector")
    _require_bool(person_detector, "enabled", "perception.person_detector.enabled")
    _require_string(person_detector, "backend", "perception.person_detector.backend")
    _require_string(person_detector, "model_name", "perception.person_detector.model_name")
    confidence = _require_number(
        person_detector,
        "confidence_threshold",
        "perception.person_detector.confidence_threshold",
    )
    if not 0.0 <= confidence <= 1.0:
        raise ConfigurationValidationError(
            "'perception.person_detector.confidence_threshold' must be between 0 and 1."
        )

    marker_detector = _require_section(perception, "marker_detector")
    _require_bool(marker_detector, "enabled", "perception.marker_detector.enabled")
    _require_string(marker_detector, "backend", "perception.marker_detector.backend")
    _require_string(marker_detector, "dictionary", "perception.marker_detector.dictionary")
    _require_positive_number(
        marker_detector,
        "marker_length_m",
        "perception.marker_detector.marker_length_m",
    )

    _require_bool(obstacle_avoidance, "enabled", "obstacle_avoidance.enabled")
    _require_string(obstacle_avoidance, "kind", "obstacle_avoidance.kind")
    _require_positive_number(obstacle_avoidance, "weight", "obstacle_avoidance.weight")
    _require_positive_number(obstacle_avoidance, "clearance_m", "obstacle_avoidance.clearance_m")
    _require_positive_int(
        obstacle_avoidance,
        "population_size",
        "obstacle_avoidance.population_size",
    )
    _require_positive_int(
        obstacle_avoidance,
        "max_iterations",
        "obstacle_avoidance.max_iterations",
    )
