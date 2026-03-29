from __future__ import annotations

import pytest

from manipulator_framework.infrastructure.config.schema import (
    ConfigurationValidationError,
    validate_config_dict,
)


def test_validate_config_dict_accepts_valid_config() -> None:
    config = {
        "app": {
            "name": "framework",
            "mode": "simulation",
            "use_case": "run_joint_trajectory",
        },
        "runtime": {
            "dt": 0.01,
            "max_steps": 100,
            "save_runtime_series": True,
        },
        "logging": {
            "level": "INFO",
            "save_to_file": True,
        },
        "results": {
            "base_dir": "experiments/runs",
        },
        "experiment": {
            "name": "demo",
            "seed": 42,
            "tags": [],
            "notes": "",
        },
        "scenario": {
            "name": "synthetic_joint_trajectory",
        },
        "controller": {
            "kind": "joint_pd",
            "gains": {"kp": 10.0, "kd": 1.0, "ki": 0.0},
            "limits": {"max_velocity": 1.0, "max_acceleration": 2.0},
        },
        "planning": {
            "kind": "quintic_joint_trajectory",
            "duration": 1.0,
        },
        "visual_servoing": {
            "enabled": False,
            "kind": "pbvs",
            "target_frame": "aruco_target",
            "camera_frame": "camera",
            "gain": 0.8,
        },
        "perception": {
            "person_detector": {
                "enabled": False,
                "backend": "yolo",
                "model_name": "yolo11n",
                "confidence_threshold": 0.5,
            },
            "marker_detector": {
                "enabled": False,
                "backend": "aruco",
                "dictionary": "DICT_4X4_50",
                "marker_length_m": 0.05,
            },
        },
        "obstacle_avoidance": {
            "enabled": False,
            "kind": "cuckoo_search",
            "weight": 1.0,
            "clearance_m": 0.20,
            "population_size": 10,
            "max_iterations": 15,
        },
    }

    validate_config_dict(config)


def test_validate_config_dict_rejects_missing_section() -> None:
    config = {
        "app": {"name": "framework", "mode": "simulation", "use_case": "run_joint_trajectory"},
        "runtime": {"dt": 0.01, "max_steps": 100, "save_runtime_series": True},
        "logging": {"level": "INFO", "save_to_file": True},
        "results": {"base_dir": "experiments/runs"},
    }

    with pytest.raises(ConfigurationValidationError, match="Missing required config sections"):
        validate_config_dict(config)


def test_validate_config_dict_rejects_invalid_dt() -> None:
    config = {
        "app": {"name": "framework", "mode": "simulation", "use_case": "run_joint_trajectory"},
        "runtime": {"dt": -0.01, "max_steps": 100, "save_runtime_series": True},
        "logging": {"level": "INFO", "save_to_file": True},
        "results": {"base_dir": "experiments/runs"},
        "experiment": {"name": "demo", "seed": 42, "tags": [], "notes": ""},
        "scenario": {"name": "synthetic_joint_trajectory"},
        "controller": {
            "kind": "joint_pd",
            "gains": {"kp": 10.0, "kd": 1.0, "ki": 0.0},
            "limits": {"max_velocity": 1.0, "max_acceleration": 2.0},
        },
        "planning": {"kind": "quintic_joint_trajectory", "duration": 1.0},
        "visual_servoing": {
            "enabled": False,
            "kind": "pbvs",
            "target_frame": "aruco_target",
            "camera_frame": "camera",
            "gain": 0.8,
        },
        "perception": {
            "person_detector": {
                "enabled": False,
                "backend": "yolo",
                "model_name": "yolo11n",
                "confidence_threshold": 0.5,
            },
            "marker_detector": {
                "enabled": False,
                "backend": "aruco",
                "dictionary": "DICT_4X4_50",
                "marker_length_m": 0.05,
            },
        },
        "obstacle_avoidance": {
            "enabled": False,
            "kind": "cuckoo_search",
            "weight": 1.0,
            "clearance_m": 0.20,
            "population_size": 10,
            "max_iterations": 15,
        },
    }

    with pytest.raises(ConfigurationValidationError, match="'runtime.dt' must be positive."):
        validate_config_dict(config)
