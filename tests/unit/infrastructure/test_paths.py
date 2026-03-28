from __future__ import annotations

from manipulator_framework.infrastructure.utils.paths import build_run_id, ensure_run_dir


def test_build_run_id_uses_prefix() -> None:
    run_id = build_run_id(prefix="experiment")
    assert run_id.startswith("experiment_")


def test_ensure_run_dir_creates_expected_structure(tmp_path) -> None:
    run_dir = ensure_run_dir(str(tmp_path), "run_123")

    assert run_dir.exists()
    assert (run_dir / "artifacts").exists()
    assert (run_dir / "logs").exists()
