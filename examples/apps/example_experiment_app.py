from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeResult:
    run_id: str


class FakeExperimentUseCase:
    def execute(self, config: dict) -> FakeResult:
        print("[experiment] scenario:", config["experiment"]["name"])
        return FakeResult(run_id="experiment_run_001")


class FakeComposer:
    def __init__(self, config: dict) -> None:
        self._config = config

    def build_experiment_use_case(self) -> FakeExperimentUseCase:
        return FakeExperimentUseCase()


def main() -> int:
    config = {
        "experiment": {"name": "pbvs_with_avoidance"},
    }

    composer = FakeComposer(config)
    use_case = composer.build_experiment_use_case()
    result = use_case.execute(config)

    print("[experiment] finished:", result.run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
