from __future__ import annotations

import subprocess
import sys


def main() -> int:
    """
    Run the official main simulation app entrypoint with the base protocol config.
    """
    command = [
        sys.executable,
        "-m",
        "manipulator_framework.apps.simulation_app",
        "configs/app/pbvs_official.yaml",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
