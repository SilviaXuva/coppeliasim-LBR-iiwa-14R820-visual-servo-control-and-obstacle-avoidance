from __future__ import annotations

from manipulator_framework.infrastructure.timing.system_clock import SystemClock


def test_system_clock_now_returns_float() -> None:
    clock = SystemClock()
    value = clock.now()

    assert isinstance(value, float)


def test_system_clock_dt_returns_non_negative_float() -> None:
    clock = SystemClock()
    clock.now()
    delta = clock.dt()

    assert isinstance(delta, float)
    assert delta >= 0.0
