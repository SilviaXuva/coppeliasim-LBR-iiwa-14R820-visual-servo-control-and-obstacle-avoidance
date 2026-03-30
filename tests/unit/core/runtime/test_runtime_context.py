from __future__ import annotations

from manipulator_framework.core.runtime import RuntimeContext


def test_runtime_context_has_default_values() -> None:
    context = RuntimeContext()

    assert context.cycle_index == 0
    assert context.timestamp == 0.0
    assert context.robot_state is None
    assert context.trajectory_reference is None
