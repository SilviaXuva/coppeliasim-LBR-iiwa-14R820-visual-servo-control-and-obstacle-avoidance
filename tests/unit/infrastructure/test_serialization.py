from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manipulator_framework.infrastructure.utils.serialization import to_serializable


@dataclass
class DemoData:
    values: np.ndarray
    name: str


def test_to_serializable_handles_dataclass_and_numpy() -> None:
    obj = DemoData(
        values=np.array([1.0, 2.0, 3.0]),
        name="demo",
    )

    serialized = to_serializable(obj)

    assert serialized["values"] == [1.0, 2.0, 3.0]
    assert serialized["name"] == "demo"
