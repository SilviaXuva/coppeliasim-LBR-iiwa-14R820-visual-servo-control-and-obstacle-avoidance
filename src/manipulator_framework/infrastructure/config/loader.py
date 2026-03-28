from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from manipulator_framework.core.contracts.configuration_interface import ConfigurationInterface
from manipulator_framework.infrastructure.config.defaults import DEFAULT_CONFIG
from manipulator_framework.infrastructure.config.schema import validate_config_dict


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge dictionaries without losing unspecified defaults."""
    result = deepcopy(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
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
