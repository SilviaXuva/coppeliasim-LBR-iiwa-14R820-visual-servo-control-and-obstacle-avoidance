from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any


_SCENE_PATH_ENV_VAR = "COPPELIA_SCENE_PATH"


def _default_scene_path() -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    candidates = (
        repo_root / "scenes" / "4.Vision-based.ttt",
        repo_root.parent / "scenes" / "4.Vision-based.ttt",
    )
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _resolve_optional_path(value: Any, base_dir: Path | None = None) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if text == "":
        return None

    path = Path(text).expanduser()
    if path.is_absolute():
        return str(path)

    if base_dir is not None:
        return str((base_dir / path).resolve())
    return str(path.resolve())


@dataclass(slots=True)
class RuntimeConfig:
    backend: str = "mock"
    cycles: int = 1
    max_control_steps_per_cycle: int | None = None
    stop_on_success: bool = False
    random_seed: int = 42
    enable_visualization: bool = False


@dataclass(slots=True)
class PickAndPlaceConfig:
    kp: float = 1.0
    ki: float = 0.0
    trajectory_duration_s: float = 2.0
    control_dt_s: float = 0.05
    marker_search_max_steps: int = 20
    target_height_offset_m: float = 0.0
    marker_length_m: float = 0.05
    aruco_dictionary: str = "DICT_6X6_250"


@dataclass(slots=True)
class PersistenceConfig:
    output_dir: str = "manipulator_framework/results"
    save_json: bool = True
    save_csv: bool = True


@dataclass(slots=True)
class CoppeliaConfig:
    host: str = "localhost"
    port: int = 23000
    scene_path: str | None = field(default_factory=_default_scene_path)
    robot_path: str = "./LBRiiwa14R820"
    joints_count: int = 7
    joints_prefix: str = "./joint"
    tip_path: str = "./tip"
    camera_sensor_path: str = "./camera1"
    camera_distortion_coefficients: tuple[float, ...] = ()
    camera_frame_rotation: tuple[tuple[float, ...], ...] | None = None


@dataclass(slots=True)
class ExperimentConfig:
    experiment: str = "pick_and_place"
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    pick_and_place: PickAndPlaceConfig = field(default_factory=PickAndPlaceConfig)
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)
    coppelia: CoppeliaConfig = field(default_factory=CoppeliaConfig)


def _apply_environment_overrides(config: ExperimentConfig) -> ExperimentConfig:
    scene_path_from_env = _resolve_optional_path(
        os.getenv(_SCENE_PATH_ENV_VAR)
    )
    if scene_path_from_env is not None:
        config.coppelia.scene_path = scene_path_from_env
    return config


def default_experiment_config(experiment: str) -> ExperimentConfig:
    if experiment != "pick_and_place":
        raise ValueError(
            f"Unsupported experiment '{experiment}'. Supported: ['pick_and_place']."
        )
    return _apply_environment_overrides(ExperimentConfig(experiment=experiment))


def load_experiment_config(
    experiment: str,
    config_path: str | None = None,
) -> ExperimentConfig:
    config = default_experiment_config(experiment)
    if config_path is None:
        return config

    config_file = Path(config_path).expanduser().resolve()
    data = json.loads(config_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Experiment config file must contain a JSON object.")

    merged = _deep_merge(asdict(config), data)
    return _apply_environment_overrides(
        _experiment_config_from_dict(merged, base_dir=config_file.parent)
    )


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _experiment_config_from_dict(
    data: dict[str, Any],
    base_dir: Path | None = None,
) -> ExperimentConfig:
    runtime_data = data.get("runtime", {})
    pick_data = data.get("pick_and_place", {})
    persistence_data = data.get("persistence", {})
    coppelia_data = data.get("coppelia", {})

    camera_distortion = tuple(
        float(value)
        for value in coppelia_data.get("camera_distortion_coefficients", ())
    )
    frame_rotation_value = coppelia_data.get("camera_frame_rotation")
    frame_rotation: tuple[tuple[float, ...], ...] | None = None
    if frame_rotation_value is not None:
        frame_rotation = tuple(
            tuple(float(value) for value in row)
            for row in frame_rotation_value
        )

    return ExperimentConfig(
        experiment=str(data.get("experiment", "pick_and_place")),
        runtime=RuntimeConfig(
            backend=str(runtime_data.get("backend", "mock")),
            cycles=int(runtime_data.get("cycles", 1)),
            max_control_steps_per_cycle=runtime_data.get("max_control_steps_per_cycle"),
            stop_on_success=bool(runtime_data.get("stop_on_success", False)),
            random_seed=int(runtime_data.get("random_seed", 42)),
            enable_visualization=bool(runtime_data.get("enable_visualization", False)),
        ),
        pick_and_place=PickAndPlaceConfig(
            kp=float(pick_data.get("kp", 1.0)),
            ki=float(pick_data.get("ki", 0.0)),
            trajectory_duration_s=float(pick_data.get("trajectory_duration_s", 2.0)),
            control_dt_s=float(pick_data.get("control_dt_s", 0.05)),
            marker_search_max_steps=int(pick_data.get("marker_search_max_steps", 20)),
            target_height_offset_m=float(pick_data.get("target_height_offset_m", 0.0)),
            marker_length_m=float(pick_data.get("marker_length_m", 0.05)),
            aruco_dictionary=str(pick_data.get("aruco_dictionary", "DICT_6X6_250")),
        ),
        persistence=PersistenceConfig(
            output_dir=str(
                persistence_data.get("output_dir", "manipulator_framework/results")
            ),
            save_json=bool(persistence_data.get("save_json", True)),
            save_csv=bool(persistence_data.get("save_csv", True)),
        ),
        coppelia=CoppeliaConfig(
            host=str(coppelia_data.get("host", "localhost")),
            port=int(coppelia_data.get("port", 23000)),
            scene_path=_resolve_optional_path(
                coppelia_data.get("scene_path", _default_scene_path()),
                base_dir=base_dir,
            ),
            robot_path=str(coppelia_data.get("robot_path", "./LBRiiwa14R820")),
            joints_count=int(coppelia_data.get("joints_count", 7)),
            joints_prefix=str(coppelia_data.get("joints_prefix", "./joint")),
            tip_path=str(coppelia_data.get("tip_path", "./tip")),
            camera_sensor_path=str(
                coppelia_data.get("camera_sensor_path", "./camera1")
            ),
            camera_distortion_coefficients=camera_distortion,
            camera_frame_rotation=frame_rotation,
        ),
    )
