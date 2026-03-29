from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from manipulator_framework.core.contracts.results_repository_interface import ResultsRepositoryInterface
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.infrastructure.utils.paths import ensure_run_dir
from manipulator_framework.infrastructure.utils.serialization import to_serializable


class FileSystemResultsRepository(ResultsRepositoryInterface):
    """Filesystem-backed results repository for canonical RunResult persistence."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def save_result(self, result: RunResult) -> None:
        run_dir = ensure_run_dir(self.base_dir, result.run_id)

        self._write_yaml(run_dir / "config.yaml", result.run_schema.resolved_config)
        self._write_json(run_dir / "metadata.json", result.metadata_dict())
        self._write_json(run_dir / "summary.json", result.summary_dict())
        self._write_json(run_dir / "metrics.json", result.metrics_dict())
        self._write_csv(run_dir / "metrics.csv", result.scalar_metrics_rows())

        for series_name, samples in result.series_samples_dict().items():
            self.save_timeseries(result.run_id, series_name, samples)

    def save_timeseries(
        self,
        run_id: str,
        series_name: str,
        samples: list[dict[str, Any]],
    ) -> None:
        run_dir = ensure_run_dir(self.base_dir, run_id)
        self._write_json(run_dir / f"{series_name}.json", samples)

    def save_artifact(self, run_id: str, artifact_name: str, artifact_path: str) -> None:
        run_dir = ensure_run_dir(self.base_dir, run_id)
        destination = run_dir / "artifacts" / artifact_name
        destination.parent.mkdir(parents=True, exist_ok=True)

        source = Path(artifact_path)
        shutil.copy2(source, destination)

    def _write_json(self, path: Path, payload: Any) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(to_serializable(payload), handle, indent=2, ensure_ascii=False)

    def _write_yaml(self, path: Path, payload: Any) -> None:
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(
                to_serializable(payload),
                handle,
                sort_keys=False,
                allow_unicode=True,
            )

    def _write_csv(self, path: Path, rows: list[dict[str, Any]]) -> None:
        fieldnames = ("name", "value", "unit", "description")
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({name: row.get(name, "") for name in fieldnames})
