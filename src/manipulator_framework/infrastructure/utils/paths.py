from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def build_run_id(prefix: str = "run") -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"


def ensure_run_dir(base_dir: str, run_id: str) -> Path:
    run_dir = Path(base_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    (run_dir / "logs").mkdir(exist_ok=True)
    return run_dir
