from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PersistenceConfig:
    output_dir: str = "manipulator_framework/results"
    save_json: bool = True
    save_csv: bool = True


def parse_persistence_config(data: Mapping[str, Any]) -> PersistenceConfig:
    return PersistenceConfig(
        output_dir=str(
            data.get("output_dir", "manipulator_framework/results")
        ),
        save_json=bool(data.get("save_json", True)),
        save_csv=bool(data.get("save_csv", True)),
    )
