from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from manipulator_framework.application.dto.run_requests import RunPBVSProtocolRequest
from manipulator_framework.application.use_cases.run_pbvs_protocol import RunPBVSProtocol


@dataclass
class _FakeRunResult:
    success: bool
    summary: dict[str, object]


@dataclass
class _FakeRunResponse:
    run_result: _FakeRunResult


class _FakePBVSUseCase:
    def execute(self, _request):
        return _FakeRunResponse(
            run_result=_FakeRunResult(
                success=True,
                summary={
                    "final_visual_error": 0.01,
                    "minimum_clearance": 0.25,
                },
            )
        )


class _FakeComposer:
    def __init__(self, *, config, sim_client):
        self.config = config
        self.sim_client = sim_client

    def build_run_pbvs_with_avoidance(self):
        return _FakePBVSUseCase()


class _FakeConfigLoader:
    def __init__(self, protocol: dict, app_config: dict):
        self._protocol = protocol
        self._app_config = app_config

    def load(self, _path: str) -> dict:
        return dict(self._protocol)

    def load_and_resolve(self, _path: str) -> dict:
        return dict(self._app_config)


class _FakeCompareRuns:
    def __init__(self) -> None:
        self.received_run_ids: tuple[str, ...] | None = None

    def execute(self, run_ids: tuple[str, ...]) -> int:
        self.received_run_ids = run_ids
        return 0


def test_run_pbvs_protocol_executes_all_seeds_and_compares() -> None:
    unique = uuid4().hex
    app_config_path = Path(f"app_config_{unique}.yaml")
    protocol_path = Path(f"protocol_config_{unique}.yaml")
    app_config_path.write_text("app: {}", encoding="utf-8")
    protocol_path.write_text("protocol: {}", encoding="utf-8")

    protocol = {
        "name": "base_protocol",
        "app_config": str(app_config_path),
        "repetitions": 2,
        "seeds": [101, 202],
        "resolved_config": {"planning": {"duration": 1.5}},
    }
    app_config = {
        "planning": {"duration": 1.0, "enable_avoidance": True},
        "simulation": {"host": "127.0.0.1"},
    }
    compare_runs = _FakeCompareRuns()

    try:
        use_case = RunPBVSProtocol(
            config_loader=_FakeConfigLoader(protocol=protocol, app_config=app_config),
            compare_runs_use_case=compare_runs,
            sim_client_factory=lambda _cfg: object(),
            composer_factory=_FakeComposer,
        )

        response = use_case.execute(
            RunPBVSProtocolRequest(protocol_path=str(protocol_path))
        )

        assert response.protocol_name == "base_protocol"
        assert response.repetitions == 2
        assert response.run_ids == (
            "base_protocol_rep_1_seed_101",
            "base_protocol_rep_2_seed_202",
        )
        assert all(run.success for run in response.runs)
        assert compare_runs.received_run_ids == response.run_ids
    finally:
        if app_config_path.exists():
            app_config_path.unlink()
        if protocol_path.exists():
            protocol_path.unlink()


def test_run_pbvs_protocol_does_not_connect_coppelia_for_pyplot_backend() -> None:
    unique = uuid4().hex
    app_config_path = Path(f"app_config_{unique}.yaml")
    protocol_path = Path(f"protocol_config_{unique}.yaml")
    app_config_path.write_text("app: {}", encoding="utf-8")
    protocol_path.write_text("protocol: {}", encoding="utf-8")

    protocol = {
        "name": "pyplot_protocol",
        "app_config": str(app_config_path),
        "repetitions": 1,
        "seeds": [11],
        "resolved_config": {},
    }
    app_config = {
        "planning": {"duration": 1.0, "enable_avoidance": True},
        "simulation": {"backend": "pyplot"},
    }
    compare_runs = _FakeCompareRuns()
    calls = {"connect": 0}

    def _sim_client_factory(_cfg):
        calls["connect"] += 1
        return object()

    try:
        use_case = RunPBVSProtocol(
            config_loader=_FakeConfigLoader(protocol=protocol, app_config=app_config),
            compare_runs_use_case=compare_runs,
            sim_client_factory=_sim_client_factory,
            composer_factory=_FakeComposer,
        )

        response = use_case.execute(
            RunPBVSProtocolRequest(protocol_path=str(protocol_path))
        )

        assert response.run_ids == ("pyplot_protocol_rep_1_seed_11",)
        assert calls["connect"] == 0
    finally:
        if app_config_path.exists():
            app_config_path.unlink()
        if protocol_path.exists():
            protocol_path.unlink()
