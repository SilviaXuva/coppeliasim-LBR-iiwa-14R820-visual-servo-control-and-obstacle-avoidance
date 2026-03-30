from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from manipulator_framework.core.contracts import ResultsRepositoryInterface
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.infrastructure.utils.paths import ensure_run_dir
from manipulator_framework.infrastructure.utils.serialization import to_serializable


class FileSystemResultsRepository(ResultsRepositoryInterface):
    """
    Filesystem-backed results repository for scientific reproducibility.
    Follows the canonical directory structure:
    runs/<run_id>/[logs/, artifacts/, config.yaml, metadata.json, metrics.csv, summary.json].
    """
    REQUIRED_RUN_FILES = ("config.yaml", "metadata.json", "metrics.csv", "summary.json")

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def save_run(self, result: RunResult) -> None:
        run_dir = ensure_run_dir(self.base_dir, result.run_id)
        artifacts_dir = run_dir / "artifacts"
        logs_dir = run_dir / "logs"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        self._write_required_run_files(run_dir=run_dir, result=result)
        self._write_json(run_dir / "metrics.json", result.metrics_dict())

        runtime_cycles = [
            {
                "cycle_index": cycle.cycle_index,
                "timestamp": cycle.timestamp,
                "success": cycle.success,
                "observations": cycle.observations,
                "commands": cycle.commands,
                "metrics_delta": cycle.metrics_delta,
                "events": list(cycle.events),
                "errors": list(cycle.errors),
            }
            for cycle in result.cycle_results
        ]
        self._write_json(run_dir / "runtime_cycles.json", runtime_cycles)

        for series_name, samples in result.series_samples_dict().items():
            self._write_json(run_dir / f"{series_name}.json", samples)

        artifacts_manifest = self._save_artifacts(result=result, artifacts_dir=artifacts_dir)
        self._write_json(run_dir / "artifacts_manifest.json", artifacts_manifest)

        self._write_lines(
            logs_dir / "run.log",
            self._build_minimum_log_lines(result=result, artifacts_manifest=artifacts_manifest),
        )

    def _write_required_run_files(self, *, run_dir: Path, result: RunResult) -> None:
        self._write_yaml(run_dir / "config.yaml", result.resolved_config)
        self._write_json(run_dir / "metadata.json", result.metadata_dict())
        self._write_json(run_dir / "summary.json", result.summary_dict())
        self._write_csv(run_dir / "metrics.csv", result.scalar_metrics_rows())

    def _save_artifacts(self, result: RunResult, artifacts_dir: Path) -> list[dict[str, Any]]:
        manifest: list[dict[str, Any]] = []
        for artifact in result.artifacts:
            source_path = Path(artifact.path)
            destination_path = artifacts_dir / artifact.name

            copied = False
            if source_path.exists() and source_path.is_file():
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, destination_path)
                copied = True

            manifest.append(
                {
                    "name": artifact.name,
                    "kind": artifact.kind,
                    "description": artifact.description,
                    "source_path": str(source_path),
                    "stored_path": str(destination_path if copied else ""),
                    "copied": copied,
                }
            )
        return manifest

    def _build_minimum_log_lines(
        self,
        *,
        result: RunResult,
        artifacts_manifest: list[dict[str, Any]],
    ) -> list[str]:
        scenario_name = (
            str(result.summary.get("scenario_name", "")).strip()
            or str(result.resolved_config.get("scenario", {}).get("name", "")).strip()
            or str(result.resolved_config.get("scenario_name", "")).strip()
            or "unknown"
        )

        lines = [
            f"run_id={result.run_id}",
            f"seed={result.seed}",
            f"scenario={scenario_name}",
            f"success={result.success}",
            f"num_cycles={result.num_cycles}",
            f"start_time={result.start_time}",
            f"end_time={result.end_time}",
            f"artifacts={sum(1 for item in artifacts_manifest if item.get('copied'))}/{len(artifacts_manifest)}",
        ]

        if result.cycle_results:
            last_cycle = result.cycle_results[-1]
            lines.append(f"last_cycle_index={last_cycle.cycle_index}")
            lines.append(f"last_cycle_success={last_cycle.success}")
            lines.append(f"last_cycle_errors={len(last_cycle.errors)}")

        return lines

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

    def _write_lines(self, path: Path, lines: list[str]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(f"{line}\n")
