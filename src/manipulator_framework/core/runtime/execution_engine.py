from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.core.contracts import ClockInterface, ExecutionEngineInterface
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric, TimeSeriesSample, compute_success_rate
from manipulator_framework.core.types import CycleResult
from .pipeline import RuntimePipeline
from .runtime_context import RuntimeContext


@dataclass
class ExecutionEngine(ExecutionEngineInterface):
    """
    Pure execution engine responsible for orchestrating the runtime pipeline.
    Produces canonical CycleResult instances for each step.
    """
    clock: ClockInterface
    pipeline: RuntimePipeline
    sampling_period_s: float | None = None
    _cycle_index: int = field(default=0, init=False, repr=False)

    def set_pipeline(self, pipeline: RuntimePipeline) -> None:
        self.pipeline = pipeline

    def set_sampling_period(self, sampling_period_s: float) -> None:
        if sampling_period_s <= 0.0:
            raise ValueError("sampling_period_s must be greater than zero.")
        self.sampling_period_s = float(sampling_period_s)

    def step(self) -> CycleResult:
        timestamp = self.clock.now()

        context = RuntimeContext(
            cycle_index=self._cycle_index,
            timestamp=timestamp,
        )

        step_results = self.pipeline.run_cycle(context)
        success = all(result.success for result in step_results)

        events = tuple(f"{result.step_name}: {result.message}" for result in step_results)
        errors = tuple(result.message for result in step_results if not result.success)

        observations = {
            "has_robot_state": context.robot_state is not None,
            "has_camera_frame": context.camera_frame is not None,
            "num_marker_detections": len(context.marker_detections),
            "num_person_detections": len(context.person_detections),
            "num_tracked_targets": len(context.tracked_targets),
            "num_obstacles": len(context.obstacles),
        }

        commands: dict[str, Any] = {}
        if context.control_output is not None and context.control_output.joint_command is not None:
            commands["joint_command"] = list(context.control_output.joint_command.values.tolist())
            commands["joint_command_mode"] = context.control_output.joint_command.mode.value

        metrics_delta_raw = context.metadata.get("cycle_metrics", {})
        metrics_delta: dict[str, float] = {}
        if isinstance(metrics_delta_raw, dict):
            for key, value in metrics_delta_raw.items():
                if isinstance(value, (int, float)):
                    metrics_delta[key] = float(value)

        cycle_result = CycleResult(
            cycle_index=self._cycle_index,
            timestamp=timestamp,
            success=success,
            observations=observations,
            commands=commands,
            metrics_delta=metrics_delta,
            events=events,
            errors=errors,
        )

        self._cycle_index += 1
        return cycle_result

    def run(
        self,
        *,
        run_id: str,
        resolved_config: dict[str, Any],
        seed: int,
        num_cycles: int = 1,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> RunResult:
        if num_cycles <= 0:
            raise ValueError("num_cycles must be greater than zero.")

        started_at = self.clock.now() if start_time is None else float(start_time)
        results: list[CycleResult] = []
        for cycle in range(num_cycles):
            if self.sampling_period_s is not None:
                cycle_target_time = started_at + (cycle * self.sampling_period_s)
                self.clock.sleep_until(cycle_target_time)
            results.append(self.step())

        if end_time is None:
            if self.sampling_period_s is not None:
                finished_at = started_at + (num_cycles * self.sampling_period_s)
            else:
                finished_at = self.clock.now()
        else:
            finished_at = float(end_time)
        success_flags = [result.success for result in results]
        success = bool(success_flags) and all(success_flags)

        success_metric = compute_success_rate(success_flags)
        runtime_series = tuple(
            TimeSeriesSample(
                t=cycle_result.timestamp,
                values={
                    "success": 1.0 if cycle_result.success else 0.0,
                    "events": float(len(cycle_result.events)),
                    "errors": float(len(cycle_result.errors)),
                    **cycle_result.metrics_delta,
                },
            )
            for cycle_result in results
        )

        final_cycle_metrics = dict(results[-1].metrics_delta)
        scalar_metrics = [
            success_metric,
            ScalarMetric(
                name="num_cycles",
                value=float(len(results)),
                unit="cycles",
            ),
        ]
        if "visual_error" in final_cycle_metrics:
            scalar_metrics.append(
                ScalarMetric(
                    name="visual_error",
                    value=float(final_cycle_metrics["visual_error"]),
                    unit="m",
                    description="Final visual servo error norm.",
                )
            )
        if "joint_error" in final_cycle_metrics:
            scalar_metrics.append(
                ScalarMetric(
                    name="joint_error",
                    value=float(final_cycle_metrics["joint_error"]),
                    unit="rad",
                    description="Final joint error norm.",
                )
            )
        if "success" in final_cycle_metrics:
            scalar_metrics.append(
                ScalarMetric(
                    name="success",
                    value=float(final_cycle_metrics["success"]),
                    unit="ratio",
                    description="Success from visual_error < threshold.",
                )
            )

        summary = {
            "final_cycle_index": results[-1].cycle_index,
            "final_cycle_success": results[-1].success,
            "total_errors": sum(len(result.errors) for result in results),
        }
        if self.sampling_period_s is not None:
            summary["sampling_period_s"] = float(self.sampling_period_s)
            summary["sampling_frequency_hz"] = float(1.0 / self.sampling_period_s)
        if "visual_error" in final_cycle_metrics:
            summary["final_visual_error"] = float(final_cycle_metrics["visual_error"])
        if "joint_error" in final_cycle_metrics:
            summary["final_joint_error"] = float(final_cycle_metrics["joint_error"])
        if "success" in final_cycle_metrics:
            summary["visual_success"] = bool(final_cycle_metrics["success"] >= 1.0)

        return RunResult(
            run_id=run_id,
            success=success,
            num_cycles=len(results),
            summary=summary,
            metrics=MetricsSnapshot(
                scalar_metrics=tuple(scalar_metrics),
                series={"runtime_cycles": runtime_series},
            ),
            resolved_config=dict(resolved_config),
            seed=int(seed),
            start_time=started_at,
            end_time=finished_at,
            cycle_results=tuple(results),
        )

    def reset(self) -> None:
        self._cycle_index = 0
