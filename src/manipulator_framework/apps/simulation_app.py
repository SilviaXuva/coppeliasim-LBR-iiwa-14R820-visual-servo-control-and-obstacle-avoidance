from __future__ import annotations

from manipulator_framework.application.composition.simulation_composer import (
    SimulationComposer,
)
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main() -> int:
    """Run the simulation app entrypoint."""
    loader = YAMLConfigurationLoader()
    raw_config = loader.load("configs/app/simulation.yaml")
    config = loader.resolve(raw_config)

    composer = SimulationComposer(config=config)
    use_case = composer.build_simulation_use_case()

    result = use_case.execute(config)

    print(f"Simulation finished. run_id={result.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
