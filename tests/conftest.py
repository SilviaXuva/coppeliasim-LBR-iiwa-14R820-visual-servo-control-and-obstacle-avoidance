from __future__ import annotations

import os
from pathlib import Path


def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
    """
    Optionally force pytest temporary base directory into the workspace.
    Disabled by default because some sandboxes mark selected workspace temp
    folders as unreadable during pytest session teardown.
    """
    if os.environ.get("MF_FORCE_BASETEMP", "0") != "1":
        return

    preferred = (Path.cwd() / ".pytest_temp").resolve()
    preferred.mkdir(parents=True, exist_ok=True)
    config.option.basetemp = str(preferred)
