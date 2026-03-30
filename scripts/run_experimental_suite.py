from __future__ import annotations

import subprocess
import sys


def main() -> int:
    """
    Run the official experimental test scope for clean-environment reproducibility.
    """
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit",
        "tests/integration",
        "tests/regression",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
