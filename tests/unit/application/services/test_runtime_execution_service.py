from __future__ import annotations

from manipulator_framework.application.dto.run_requests import RunJointTrajectoryRequest
from manipulator_framework.application.services.runtime_execution_service import RuntimeExecutionService
from tests.fixtures.application_fakes import FakeClock, FakeExecutionEngine


def test_runtime_execution_service_configures_engine_sampling_period_when_supported() -> None:
    clock = FakeClock(start_time=0.0, step_dt=0.05)
    service = RuntimeExecutionService(clock=clock)
    engine = FakeExecutionEngine()

    captured: dict[str, float] = {}

    def _set_sampling_period(dt: float) -> None:
        captured["dt"] = float(dt)

    engine.set_sampling_period = _set_sampling_period  # type: ignore[attr-defined]

    run_result = service.execute(
        execution_engine=engine,
        request=RunJointTrajectoryRequest(
            run_id="runtime_service_sampling_test",
            config={},
            seed=7,
            duration=0.2,
        ),
        duration=0.2,
    )

    assert captured["dt"] == 0.05
    assert run_result.summary["planned_dt"] == 0.05
    assert run_result.summary["planned_num_cycles"] == 4

