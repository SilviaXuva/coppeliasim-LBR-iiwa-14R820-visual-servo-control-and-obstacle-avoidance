from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConfigurationPaths:
    """
    Resolved configuration file paths grouped by domain.
    """
    app_config: Path
    controller_config: Path | None = None
    visual_servoing_config: Path | None = None
    perception_config: Path | None = None
    obstacle_avoidance_config: Path | None = None
    experiment_config: Path | None = None
