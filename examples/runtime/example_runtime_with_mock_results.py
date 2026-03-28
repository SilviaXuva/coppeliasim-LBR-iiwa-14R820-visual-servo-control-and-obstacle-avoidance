from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.runtime import (
    ExecutionEngine,
    PipelineStep,
    RuntimeContext,
    RuntimePipeline,
    StepResult,
)

if __package__ in (None, ""):
    import pathlib
    import sys

    repo_root = pathlib.Path(__file__).resolve().parents[2]
    sys.path.append(str(repo_root / "src"))
    sys.path.append(str(repo_root))
    from examples.runtime._mocks import FakeClock  # type: ignore
else:
    from ._mocks import FakeClock


@dataclass
class AlwaysFailStep(PipelineStep):
    @property
    def name(self) -> str:
        return "always_fail"

    def run(self, context: RuntimeContext) -> StepResult:
        return StepResult(
            step_name=self.name,
            success=False,
            message="Intentional failure for runtime contract validation.",
            timestamp=context.timestamp,
        )


def main() -> None:
    pipeline = RuntimePipeline(steps=[AlwaysFailStep()])
    engine = ExecutionEngine(clock=FakeClock(), pipeline=pipeline)

    result = engine.step()
    print(result)


if __name__ == "__main__":
    main()
