from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
import json
from numbers import Real
import os
from pathlib import Path
from typing import Any


_SCENE_PATH_ENV_VAR = "COPPELIA_SCENE_PATH"
_EXPERIMENT_PICK_AND_PLACE_KIN_PI = "pick_and_place_kin_pi"
_EXPERIMENT_PICK_AND_PLACE_DYN_PD = "pick_and_place_dyn_pd"
_SUPPORTED_EXPERIMENTS = (
    _EXPERIMENT_PICK_AND_PLACE_KIN_PI,
    _EXPERIMENT_PICK_AND_PLACE_DYN_PD,
)

_DEFAULT_PICK_AND_PLACE_KIN_PI_KP = (
    1.64725,
    1.40056,
    1.40056,
    1.33690,
    1.36873,
    1.40056,
    1.36873,
)
_DEFAULT_PICK_AND_PLACE_KIN_PI_KI = (
    1.23544,
    0.93371,
    0.93371,
    0.89127,
    0.91249,
    0.93371,
    0.91249,
)
_DEFAULT_PICK_AND_PLACE_DYN_PD_KP = (
    80.00,
    85.00,
    25.00,
    19.00,
    10.00,
    20.00,
    5.00
)
_DEFAULT_PICK_AND_PLACE_DYN_PD_KV = (
    1.000,
    10.50,
    1.000,
    3.000,
    1.000,
    1.500,
    0.25,
)
_DEFAULT_PICK_AND_PLACE_TAU_MIN = (
    -176.00,
    -176.00,
    -100.00,
    -100.00,
    -100.00,
    -38.00,
    -38.00,
)
_DEFAULT_PICK_AND_PLACE_TAU_MAX = (
    176.00,
    176.00,
    100.00,
    100.00,
    100.00,
    38.00,
    38.00,
)

GainConfig = float | tuple[float, ...]


def _default_camera_frame_rotation() -> tuple[tuple[float, ...], ...]:
    # Legacy-compatible frame correction used for ArUco pose estimation in Coppelia.
    # Equivalent to a +180deg yaw rotation in the camera frame.
    return (
        (-1.0, 0.0, 0.0, 0.0),
        (0.0, -1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


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


def _parse_gain(value: Any, gain_name: str) -> GainConfig:
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, (str, bytes)):
        raise ValueError(
            f"`{gain_name}` must be a numeric scalar or a sequence of numeric values."
        )
    if isinstance(value, Sequence):
        if len(value) == 0:
            raise ValueError(f"`{gain_name}` sequence must not be empty.")
        try:
            return tuple(float(item) for item in value)
        except (TypeError, ValueError):
            raise ValueError(
                f"`{gain_name}` must be a numeric scalar or a sequence of numeric values."
            ) from None
    raise ValueError(
        f"`{gain_name}` must be a numeric scalar or a sequence of numeric values."
    )


def _parse_vector(value: Any, values_name: str) -> tuple[float, ...]:
    if isinstance(value, (str, bytes)):
        raise ValueError(f"`{values_name}` must be a sequence of numeric values.")
    if not isinstance(value, Sequence):
        raise ValueError(f"`{values_name}` must be a sequence of numeric values.")
    if len(value) == 0:
        raise ValueError(f"`{values_name}` must not be empty.")
    try:
        return tuple(float(item) for item in value)
    except (TypeError, ValueError):
        raise ValueError(
            f"`{values_name}` must be a sequence of numeric values."
        ) from None


def _normalize_experiment_name(experiment: str) -> str:
    normalized = {"pick_and_place": _EXPERIMENT_PICK_AND_PLACE_KIN_PI}.get(experiment, experiment)
    if normalized not in _SUPPORTED_EXPERIMENTS:
        supported = ", ".join(f"'{name}'" for name in _SUPPORTED_EXPERIMENTS)
        raise ValueError(
            f"Unsupported experiment '{experiment}'. Supported: [{supported}]."
        )
    return normalized


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
    kp: GainConfig = _DEFAULT_PICK_AND_PLACE_KIN_PI_KP
    ki: GainConfig = _DEFAULT_PICK_AND_PLACE_KIN_PI_KI
    kv: GainConfig = _DEFAULT_PICK_AND_PLACE_DYN_PD_KV
    tau_min: tuple[float, ...] = _DEFAULT_PICK_AND_PLACE_TAU_MIN
    tau_max: tuple[float, ...] = _DEFAULT_PICK_AND_PLACE_TAU_MAX
    trajectory_duration_s: float = 1.5
    control_dt_s: float = 0.05
    target_height_offset_m: float = 0.15
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
    camera_frame_rotation: tuple[tuple[float, ...], ...] | None = field(
        default_factory=_default_camera_frame_rotation
    )


@dataclass(slots=True)
class ExperimentConfig:
    experiment: str = _EXPERIMENT_PICK_AND_PLACE_KIN_PI
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
    normalized_experiment = _normalize_experiment_name(str(experiment))
    
    if normalized_experiment == _EXPERIMENT_PICK_AND_PLACE_DYN_PD:
        pick_cfg = PickAndPlaceConfig(
            kp=_DEFAULT_PICK_AND_PLACE_DYN_PD_KP,
            ki=_DEFAULT_PICK_AND_PLACE_KIN_PI_KI,
            kv=_DEFAULT_PICK_AND_PLACE_DYN_PD_KV,
        )
    else:
        pick_cfg = PickAndPlaceConfig(
            kp=_DEFAULT_PICK_AND_PLACE_KIN_PI_KP,
            ki=_DEFAULT_PICK_AND_PLACE_KIN_PI_KI,
            kv=_DEFAULT_PICK_AND_PLACE_DYN_PD_KV,
        )

    return _apply_environment_overrides(
        ExperimentConfig(experiment=normalized_experiment, pick_and_place=pick_cfg)
    )


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

    return ExperimentConfig(
        experiment=_normalize_experiment_name(
            str(data.get("experiment", _EXPERIMENT_PICK_AND_PLACE_KIN_PI))
        ),
        runtime=RuntimeConfig(
            backend=str(runtime_data.get("backend", "mock")),
            cycles=int(runtime_data.get("cycles", 1)),
            max_control_steps_per_cycle=runtime_data.get("max_control_steps_per_cycle"),
            stop_on_success=bool(runtime_data.get("stop_on_success", False)),
            random_seed=int(runtime_data.get("random_seed", 42)),
            enable_visualization=bool(runtime_data.get("enable_visualization", False)),
        ),
        pick_and_place=PickAndPlaceConfig(
            kp=_parse_gain(
                pick_data.get("kp", _DEFAULT_PICK_AND_PLACE_KIN_PI_KP),
                "kp",
            ),
            ki=_parse_gain(
                pick_data.get("ki", _DEFAULT_PICK_AND_PLACE_KIN_PI_KI),
                "ki",
            ),
            kv=_parse_gain(
                pick_data.get("kv", _DEFAULT_PICK_AND_PLACE_DYN_PD_KV),
                "kv",
            ),
            tau_min=_parse_vector(
                pick_data.get("tau_min", _DEFAULT_PICK_AND_PLACE_TAU_MIN),
                "tau_min",
            ),
            tau_max=_parse_vector(
                pick_data.get("tau_max", _DEFAULT_PICK_AND_PLACE_TAU_MAX),
                "tau_max",
            ),
            trajectory_duration_s=float(pick_data.get("trajectory_duration_s", 2.0)),
            control_dt_s=float(pick_data.get("control_dt_s", 0.05)),
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
            # Fixed for pick-and-place to preserve legacy camera frame convention.
            camera_frame_rotation=_default_camera_frame_rotation(),
        ),
    )
