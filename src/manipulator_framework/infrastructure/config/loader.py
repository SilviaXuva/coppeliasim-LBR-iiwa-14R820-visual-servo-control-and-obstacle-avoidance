from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from manipulator_framework.core.contracts.configuration_interface import ConfigurationInterface
from manipulator_framework.infrastructure.config.defaults import DEFAULT_CONFIG
from manipulator_framework.infrastructure.config.models import ConfigurationPaths
from manipulator_framework.infrastructure.config.schema import validate_config_dict


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge dictionaries without losing unspecified defaults."""
    result = deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


class YAMLConfigurationLoader(ConfigurationInterface):
    """Load raw YAML config and resolve it against validated defaults."""

    def load(self, source: str) -> dict[str, Any]:
        path = Path(source)
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def resolve(self, config: dict[str, Any]) -> dict[str, Any]:
        resolved = deep_merge(DEFAULT_CONFIG, config)
        validate_config_dict(resolved)
        return resolved

    def load_and_resolve(self, source: str) -> dict[str, Any]:
        raw_config = self.load(source)
        return self.resolve(raw_config)

    def resolve_from_paths(self, paths: ConfigurationPaths) -> dict[str, Any]:
        resolved = deepcopy(DEFAULT_CONFIG)

        for path in (
            paths.app_config,
            paths.controller_config,
            paths.visual_servoing_config,
            paths.perception_config,
            paths.obstacle_avoidance_config,
            paths.experiment_config,
        ):
            if path is None:
                continue
            resolved = deep_merge(resolved, self.load(str(path)))

        validate_config_dict(resolved)
        return resolved
