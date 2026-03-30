from __future__ import annotations

from manipulator_framework.application.composition.simulation_composer import (
    SimulationComposer,
)
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main(config_path: str = "configs/app/benchmark.yaml") -> int:
    """Run the benchmark app entrypoint."""
    loader = YAMLConfigurationLoader()
    raw_config = loader.load(config_path)
    config = loader.resolve(raw_config)

    composer = SimulationComposer(config=config)
    use_case = composer.build_benchmark_use_case()

    response = use_case.execute(config)

    print(f"Benchmark finished. compared_methods={len(response.summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
