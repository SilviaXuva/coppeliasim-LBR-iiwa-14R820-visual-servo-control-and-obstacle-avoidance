from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeResult:
    run_id: str


class FakeSimulationUseCase:
    def execute(self, config: dict) -> FakeResult:
        print("[simulation] executing use case with config:", config["app"]["name"])
        return FakeResult(run_id="simulation_run_001")


class FakeSimulationComposer:
    def __init__(self, config: dict) -> None:
        self._config = config

    def build_simulation_use_case(self) -> FakeSimulationUseCase:
        return FakeSimulationUseCase()


def main() -> int:
    config = {
        "app": {"name": "simulation_app"},
    }

    composer = FakeSimulationComposer(config=config)
    use_case = composer.build_simulation_use_case()
    result = use_case.execute(config)

    print("[simulation] finished:", result.run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
