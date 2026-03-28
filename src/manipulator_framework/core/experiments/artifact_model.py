from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunArtifact:
    name: str
    path: str
    kind: str
    description: str = ""
