from __future__ import annotations

from collections.abc import Mapping, Sequence
import csv
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


class ResultsRepository:
    """Persists experiment artifacts in simple JSON/CSV files."""

    _TIMESERIES_FIELDNAMES = (
        "run_id",
        "cycle_index",
        "step_index",
        "t_s",
        "controller",
        "target_marker_id",
        "q_error_l2",
        "q_error_linf",
        "dq_ref_l2",
        "dq_cmd_l2",
        "dq_meas_l2",
        "tau_cmd_l2",
        "tau_cmd_max_abs",
        "tau_saturated_count",
    )

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def prepare_run_dir(
        self,
        experiment: str,
        run_id: str,
    ) -> Path:
        run_dir = self._base_dir / experiment / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def save_experiment_results(
        self,
        experiment: str,
        config: Mapping[str, Any],
        metrics: Mapping[str, Any],
        cycles_rows: Sequence[Mapping[str, Any]],
        *,
        summary: Mapping[str, Any] | None = None,
        config_snapshot: Mapping[str, Any] | None = None,
        timeseries_rows: Sequence[Mapping[str, Any]] | None = None,
        events: Mapping[str, Any] | None = None,
        run_id: str | None = None,
        save_json: bool = True,
        save_csv: bool = True,
    ) -> dict[str, str]:
        # Kept for API compatibility. The v1 artifact schema always persists 5 files.
        del save_json, save_csv
        resolved_run_id = run_id or uuid4().hex[:12]
        run_dir = self.prepare_run_dir(experiment, resolved_run_id)

        artifacts: dict[str, str] = {"run_dir": str(run_dir)}

        summary_payload = (
            dict(summary)
            if summary is not None
            else self._summary_fallback(
                experiment=experiment,
                run_id=resolved_run_id,
                metrics=metrics,
            )
        )
        config_snapshot_payload = (
            dict(config_snapshot)
            if config_snapshot is not None
            else {
                "schema_version": "1.0",
                "run_id": resolved_run_id,
                "experiment_config": dict(config),
            }
        )
        timeseries_payload = (
            list(timeseries_rows)
            if timeseries_rows is not None
            else self._timeseries_fallback(
                run_id=resolved_run_id,
                cycles_rows=cycles_rows,
            )
        )
        events_payload = (
            dict(events)
            if events is not None
            else {
                "schema_version": "1.0",
                "run_id": resolved_run_id,
                "events": [],
            }
        )

        summary_path = run_dir / "summary.json"
        config_snapshot_path = run_dir / "config_snapshot.json"
        metrics_path = run_dir / "metrics.json"
        timeseries_path = run_dir / "timeseries.csv"
        events_path = run_dir / "events.json"

        self._write_json(summary_path, summary_payload)
        self._write_json(config_snapshot_path, config_snapshot_payload)
        self._write_json(metrics_path, dict(metrics))
        self._write_rows_csv(
            timeseries_path,
            timeseries_payload,
            fieldnames=self._TIMESERIES_FIELDNAMES,
        )
        self._write_json(events_path, events_payload)

        artifacts["summary_json"] = str(summary_path)
        artifacts["config_snapshot_json"] = str(config_snapshot_path)
        artifacts["metrics_json"] = str(metrics_path)
        artifacts["timeseries_csv"] = str(timeseries_path)
        artifacts["events_json"] = str(events_path)

        return artifacts

    @staticmethod
    def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def _timeseries_fallback(
        cls,
        *,
        run_id: str,
        cycles_rows: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        fallback_rows: list[dict[str, Any]] = []
        for row in cycles_rows:
            fallback_row: dict[str, Any] = {field: None for field in cls._TIMESERIES_FIELDNAMES}
            fallback_row["run_id"] = run_id
            fallback_row["cycle_index"] = row.get("cycle_index")
            fallback_row["step_index"] = row.get("executed_steps")
            fallback_row["t_s"] = None
            fallback_row["controller"] = None
            fallback_row["target_marker_id"] = row.get("target_marker_id")
            fallback_rows.append(fallback_row)
        return fallback_rows

    @staticmethod
    def _summary_fallback(
        *,
        experiment: str,
        run_id: str,
        metrics: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "run_id": run_id,
            "experiment": experiment,
            "controller": None,
            "backend": None,
            "started_at_utc": metrics.get("started_at_utc"),
            "finished_at_utc": metrics.get("finished_at_utc"),
            "duration_s": metrics.get("duration_s"),
            "cycles_planned": metrics.get("cycles_executed"),
            "cycles_executed": metrics.get("cycles_executed"),
            "success_count": metrics.get("success_count"),
            "failure_count": metrics.get("failure_count"),
            "success_rate": metrics.get("success_rate"),
            "primary_reason_counts": metrics.get("reason_counts", {}),
        }

    @staticmethod
    def _write_rows_csv(
        path: Path,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> None:
        rows_list = list(rows)
        resolved_fieldnames = list(fieldnames) if fieldnames is not None else []
        if len(resolved_fieldnames) == 0 and len(rows_list) > 0:
            resolved_fieldnames = list(rows_list[0].keys())
        if len(resolved_fieldnames) == 0:
            path.write_text("", encoding="utf-8")
            return

        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=resolved_fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows_list)
