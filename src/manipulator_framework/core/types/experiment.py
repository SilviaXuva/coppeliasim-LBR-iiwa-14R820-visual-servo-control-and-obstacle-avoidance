from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import only for type checking to avoid runtime circular imports.
    from manipulator_framework.core.experiments.result_model import RunResult

# Compatibility alias retained for callers that may import it directly.
# At runtime we lazy-load to break circular dependencies.
def _resolve_experiment_result():
    from manipulator_framework.core.experiments.result_model import RunResult as _RunResult
    return _RunResult


ExperimentResult = _resolve_experiment_result()

__all__ = ["ExperimentResult"]
