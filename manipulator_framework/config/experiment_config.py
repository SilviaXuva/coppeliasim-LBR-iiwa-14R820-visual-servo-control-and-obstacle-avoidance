from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any

from ._parsing import deep_merge, resolve_optional_path
from .controller_config import GainConfig
from .persistence_config import PersistenceConfig, parse_persistence_config
from .simulation_config import CoppeliaConfig, parse_coppelia_config
from .task_config import PickAndPlaceConfig, default_pick_and_place_config, parse_pick_and_place_config

_SCENE_PATH_ENV_VAR = "COPPELIA_SCENE_PATH"
_EXPERIMENT_PICK_AND_PLACE_KIN_PI = "pick_and_place_kin_pi"
_EXPERIMENT_PICK_AND_PLACE_DYN_PD = "pick_and_place_dyn_pd"
_SUPPORTED_EXPERIMENTS = (
    _EXPERIMENT_PICK_AND_PLACE_KIN_PI,
    _EXPERIMENT_PICK_AND_PLACE_DYN_PD,
)

__all__ = [
    "GainConfig",
    "RuntimeConfig",
    "PickAndPlaceConfig",
    "PersistenceConfig",
    "CoppeliaConfig",
    "ExperimentConfig",
    "default_experiment_config",
    "load_experiment_config",
]


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
class ExperimentConfig:
    experiment: str = _EXPERIMENT_PICK_AND_PLACE_KIN_PI
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    pick_and_place: PickAndPlaceConfig = field(
        default_factory=lambda: default_pick_and_place_config(_EXPERIMENT_PICK_AND_PLACE_KIN_PI)
    )
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)
    coppelia: CoppeliaConfig = field(default_factory=CoppeliaConfig)


def _apply_environment_overrides(config: ExperimentConfig) -> ExperimentConfig:
    scene_path_from_env = resolve_optional_path(
        os.getenv(_SCENE_PATH_ENV_VAR)
    )
    if scene_path_from_env is not None:
        config.coppelia.scene_path = scene_path_from_env
    return config


def default_experiment_config(experiment: str) -> ExperimentConfig:
    normalized_experiment = _normalize_experiment_name(str(experiment))
    pick_cfg = default_pick_and_place_config(normalized_experiment)
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

    merged = deep_merge(asdict(config), data)
    return _apply_environment_overrides(
        _experiment_config_from_dict(merged, base_dir=config_file.parent)
    )


def _experiment_config_from_dict(
    data: Mapping[str, Any],
    base_dir: Path | None = None,
) -> ExperimentConfig:
    runtime_data = data.get("runtime", {})
    pick_data = data.get("pick_and_place", {})
    persistence_data = data.get("persistence", {})
    coppelia_data = data.get("coppelia", {})

    if not isinstance(runtime_data, Mapping):
        runtime_data = {}
    if not isinstance(pick_data, Mapping):
        pick_data = {}
    if not isinstance(persistence_data, Mapping):
        persistence_data = {}
    if not isinstance(coppelia_data, Mapping):
        coppelia_data = {}

    experiment_name = _normalize_experiment_name(
        str(data.get("experiment", _EXPERIMENT_PICK_AND_PLACE_KIN_PI))
    )

    return ExperimentConfig(
        experiment=experiment_name,
        runtime=RuntimeConfig(
            backend=str(runtime_data.get("backend", "mock")),
            cycles=int(runtime_data.get("cycles", 1)),
            max_control_steps_per_cycle=runtime_data.get("max_control_steps_per_cycle"),
            stop_on_success=bool(runtime_data.get("stop_on_success", False)),
            random_seed=int(runtime_data.get("random_seed", 42)),
            enable_visualization=bool(runtime_data.get("enable_visualization", False)),
        ),
        pick_and_place=parse_pick_and_place_config(
            pick_data,
            experiment=experiment_name,
        ),
        persistence=parse_persistence_config(persistence_data),
        coppelia=parse_coppelia_config(coppelia_data, base_dir=base_dir),
    )
