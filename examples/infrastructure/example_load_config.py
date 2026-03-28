from __future__ import annotations

from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main() -> None:
    loader = YAMLConfigurationLoader()

    raw_config = loader.load("configs/app/experiment.yaml")
    resolved_config = loader.resolve(raw_config)

    print("Raw config:")
    print(raw_config)
    print()
    print("Resolved config:")
    print(resolved_config)


if __name__ == "__main__":
    main()
