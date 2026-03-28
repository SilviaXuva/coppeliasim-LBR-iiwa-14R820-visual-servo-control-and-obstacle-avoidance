from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


class SerializableMixin:
    """Provides a minimal recursive serialization contract."""

    def to_dict(self) -> dict[str, Any]:
        if not is_dataclass(self):
            raise TypeError(f"{self.__class__.__name__} must be a dataclass to use SerializableMixin.")
        return asdict(self)
