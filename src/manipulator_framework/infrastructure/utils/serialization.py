from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import numpy as np


def to_serializable(value: Any) -> Any:
    if is_dataclass(value):
        return to_serializable(asdict(value))

    if isinstance(value, dict):
        return {str(k): to_serializable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_serializable(v) for v in value]

    if hasattr(value, "__dict__"):
        return {k: to_serializable(v) for k, v in vars(value).items()}

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, (np.integer, np.floating)):
        return value.item()

    return value
