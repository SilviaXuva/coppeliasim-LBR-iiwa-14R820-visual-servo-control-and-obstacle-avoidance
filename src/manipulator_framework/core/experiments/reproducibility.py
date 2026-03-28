from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReproducibilityMetadata:
    seed: int
    code_version: str
    backend_name: str
    scenario_name: str
    timestamp_utc: str
