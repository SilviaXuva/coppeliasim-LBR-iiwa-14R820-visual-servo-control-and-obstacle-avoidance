from __future__ import annotations

from collections.abc import Mapping, Sequence
import csv
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


class ResultsRepository:
    """Persists experiment artifacts in simple JSON/CSV files."""

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save_experiment_results(
        self,
        experiment: str,
        config: Mapping[str, Any],
        metrics: Mapping[str, Any],
        cycles_rows: Sequence[Mapping[str, Any]],
        *,
        run_id: str | None = None,
        save_json: bool = True,
        save_csv: bool = True,
    ) -> dict[str, str]:
        resolved_run_id = run_id or uuid4().hex[:12]
        run_dir = self._base_dir / experiment / resolved_run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        artifacts: dict[str, str] = {"run_dir": str(run_dir)}

        if save_json:
            config_path = run_dir / "config.json"
            metrics_path = run_dir / "metrics.json"
            config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            metrics_path.write_text(
                json.dumps(metrics, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            artifacts["config_json"] = str(config_path)
            artifacts["metrics_json"] = str(metrics_path)

        if save_csv:
            cycles_path = run_dir / "cycles.csv"
            self._write_rows_csv(cycles_path, cycles_rows)
            artifacts["cycles_csv"] = str(cycles_path)

        return artifacts

    @staticmethod
    def _write_rows_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
        rows_list = list(rows)
        if len(rows_list) == 0:
            path.write_text("", encoding="utf-8")
            return

        fieldnames = list(rows_list[0].keys())
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_list)
