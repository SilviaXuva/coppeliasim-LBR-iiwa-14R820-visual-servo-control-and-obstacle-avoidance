from __future__ import annotations

from manipulator_framework.core.planning.time_parameterization import build_time_grid


def main() -> None:
    grid = build_time_grid(duration=1.0, time_step=0.3)
    print("Time grid:", grid)


if __name__ == "__main__":
    main()
