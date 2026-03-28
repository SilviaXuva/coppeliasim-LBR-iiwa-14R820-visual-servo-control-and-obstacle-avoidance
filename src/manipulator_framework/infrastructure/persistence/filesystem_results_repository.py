from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from manipulator_framework.core.contracts.results_repository_interface import ResultsRepositoryInterface
from manipulator_framework.core.types import ExperimentResult
from manipulator_framework.infrastructure.utils.paths import ensure_run_dir
from manipulator_framework.infrastructure.utils.serialization import to_serializable


class FileSystemResultsRepository(ResultsRepositoryInterface):
    """Filesystem-backed results repository."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def save_result(self, result: ExperimentResult) -> None:
        run_id = self._extract_run_id(result)
        run_dir = ensure_run_dir(self.base_dir, run_id)
        self._write_json(run_dir / "result.json", result)

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
        source = Path(artifact_path)
        shutil.copy2(source, destination)

    def _write_json(self, path: Path, payload: Any) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(to_serializable(payload), handle, indent=2, ensure_ascii=False)

    def _extract_run_id(self, result: ExperimentResult) -> str:
        """
        Placeholder policy:
        adapt this method to the real ExperimentResult shape already defined in core/types.
        """
        if hasattr(result, "run_id"):
            return str(result.run_id)

        if hasattr(result, "metadata") and isinstance(result.metadata, dict) and "run_id" in result.metadata:
            return str(result.metadata["run_id"])

        raise AttributeError(
            "ExperimentResult must expose 'run_id' directly or via result.metadata['run_id']."
        )
