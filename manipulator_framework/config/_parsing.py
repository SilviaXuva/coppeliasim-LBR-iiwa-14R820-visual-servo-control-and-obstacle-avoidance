from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Real
from pathlib import Path
from typing import Any

from .controller_config import GainConfig


def resolve_optional_path(value: Any, base_dir: Path | None = None) -> str | None:
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


def parse_gain(value: Any, gain_name: str) -> GainConfig:
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


def parse_vector(value: Any, values_name: str) -> tuple[float, ...]:
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


def parse_vector_with_size(
    value: Any,
    values_name: str,
    expected_size: int,
) -> tuple[float, ...]:
    parsed = parse_vector(value, values_name)
    if len(parsed) != expected_size:
        raise ValueError(
            f"`{values_name}` must have {expected_size} values."
        )
    return parsed


def parse_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def parse_string_sequence(value: Any, values_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        raise ValueError(f"`{values_name}` must be a sequence of strings.")
    if not isinstance(value, Sequence):
        raise ValueError(f"`{values_name}` must be a sequence of strings.")
    parsed = tuple(str(item).strip() for item in value)
    if any(item == "" for item in parsed):
        raise ValueError(f"`{values_name}` must not contain empty values.")
    return parsed


def deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, Mapping)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
