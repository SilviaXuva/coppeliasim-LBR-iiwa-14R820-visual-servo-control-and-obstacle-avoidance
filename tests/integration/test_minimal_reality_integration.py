from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from manipulator_framework.application.composition.simulation_composer import SimulationComposer
from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from manipulator_framework.adapters.stubs import StubMarkerDetector, StubPoseEstimator
from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


class _DeterministicSimClient:
    def __init__(self) -> None:
        self._joint_values = {f"LBR_iiwa_14_R820_joint{i}": 0.0 for i in range(1, 8)}
        self._t = 0.0

    def get_joint_position(self, *, robot_handle: Any, joint_name: str) -> float:
        return float(self._joint_values.get(joint_name, 0.0))

    def get_joint_velocity(self, *, robot_handle: Any, joint_name: str) -> float:
        return 0.0

    def set_joint_target_position(self, *, robot_handle: Any, joint_name: str, value: float) -> None:
        self._joint_values[joint_name] = float(value)

    def set_joint_torque(self, *, robot_handle: Any, joint_name: str, value: float) -> None:
        return None

    def get_object_position(self, *, handle: Any, reference_frame: str = "world") -> list[float]:
        return [0.5, 0.0, 0.6]

    def get_object_quaternion(self, *, handle: Any, reference_frame: str = "world") -> list[float]:
        return [0.0, 0.0, 0.0, 1.0]

    def get_sim_time(self) -> float:
        self._t += 0.01
        return self._t

    def get_camera_rgb(self, *, camera_handle: Any) -> np.ndarray:
        return np.zeros((240, 320, 3), dtype=np.uint8)

    def get_camera_intrinsics(self, *, camera_handle: Any) -> np.ndarray:
        return np.eye(3, dtype=float)

    def start_simulation(self) -> None:
        return None

    def step_simulation(self) -> None:
        self._t += 0.01

    def stop_simulation(self) -> None:
        return None


class _FakeYoloModel:
    def predict(self, image, conf: float = 0.5, verbose: bool = False):
        return []


def _base_config(results_dir: Path) -> dict[str, Any]:
    return {
        "app": {"name": "manipulator_framework", "mode": "simulation", "use_case": "run_pbvs_with_avoidance"},
        "runtime": {"dt": 0.05, "max_steps": 5, "save_runtime_series": True},
        "logging": {"level": "INFO", "save_to_file": True},
        "results": {"base_dir": str(results_dir)},
        "experiment": {"name": "minimal_reality", "seed": 7, "tags": [], "notes": ""},
        "scenario": {"name": "person_in_workspace"},
        "controller": {
            "kind": "joint_pd",
            "gains": {"kp": 10.0, "kd": 1.0, "ki": 0.0},
            "limits": {"max_velocity": 1.0, "max_acceleration": 2.0},
        },
        "planning": {"kind": "quintic_joint_trajectory", "duration": 0.15, "enable_avoidance": True},
        "visual_servoing": {"enabled": True, "kind": "pbvs", "target_frame": "aruco_target", "camera_frame": "camera", "gain": 0.7},
        "perception": {
            "person_detector": {"enabled": False, "backend": "yolo", "model_name": "yolo11n", "confidence_threshold": 0.5},
            "marker_detector": {"enabled": True, "backend": "aruco", "dictionary": "DICT_4X4_50", "marker_length_m": 0.1},
        },
        "obstacle_avoidance": {
            "enabled": True,
            "kind": "cuckoo_search",
            "weight": 1.0,
            "clearance_m": 0.2,
            "population_size": 15,
            "max_iterations": 20,
        },
        "simulation": {
            "robot_handle": "LBR_iiwa_14_R820",
            "camera_handle": "vision_sensor",
            "joint_names": [f"LBR_iiwa_14_R820_joint{i}" for i in range(1, 8)],
            "obstacle_handles": ["obs_1"],
        },
    }


def test_run_pbvs_with_avoidance_executes_end_to_end(tmp_path: Path) -> None:
    config = _base_config(tmp_path)
    composer = SimulationComposer(
        config=config,
        sim_client=_DeterministicSimClient(),
        yolo_model=_FakeYoloModel(),
    )
    use_case = composer.build_run_pbvs_with_avoidance()
    use_case.marker_detector = StubMarkerDetector()
    use_case.pose_estimator = StubPoseEstimator()

    request = RunPBVSWithAvoidanceRequest(
        run_id="e2e_pbvs_avoidance",
        config=config,
        seed=7,
        duration=0.15,
        max_cycles=3,
    )
    response = use_case.execute(request)

    assert response.run_result.success is True
    assert response.run_result.num_cycles == 3
    assert len(response.cycle_results) == 3

    run_dir = tmp_path / "e2e_pbvs_avoidance"
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "artifacts").exists()
    assert (run_dir / "logs" / "run.log").exists()


def test_simulation_composer_builds_complete_use_case() -> None:
    config = _base_config(Path("experiments/runs"))
    composer = SimulationComposer(
        config=config,
        sim_client=_DeterministicSimClient(),
        yolo_model=_FakeYoloModel(),
    )
    use_case = composer.build_run_pbvs_with_avoidance()

    assert use_case.robot is not None
    assert use_case.camera is not None
    assert use_case.marker_detector is not None
    assert use_case.pose_estimator is not None
    assert use_case.tracker is not None
    assert use_case.pbvs_controller is not None
    assert use_case.avoidance_module is not None
    assert use_case.obstacle_source is not None
    assert use_case.execution_engine is not None
    assert use_case.experiment_service is not None


def test_results_repository_persists_run_layout(tmp_path: Path) -> None:
    artifact_source = tmp_path / "artifact.txt"
    artifact_source.write_text("artifact payload", encoding="utf-8")

    run_result = RunResult(
        run_id="layout_run_001",
        success=True,
        num_cycles=2,
        summary={
            "experiment_name": "layout_validation",
            "scenario_name": "person_in_workspace",
            "backend_name": "simulation",
        },
        metrics=MetricsSnapshot(
            scalar_metrics=(ScalarMetric(name="success_rate", value=1.0, unit="ratio"),),
        ),
        artifacts=(RunArtifact(name="artifact.txt", path=str(artifact_source), kind="text"),),
        resolved_config={"runtime": {"dt": 0.05}},
        seed=123,
        start_time=0.0,
        end_time=0.1,
    )

    repository = FileSystemResultsRepository(base_dir=str(tmp_path))
    repository.save_run(run_result)

    run_dir = tmp_path / "layout_run_001"
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "artifacts").exists()
    assert (run_dir / "artifacts" / "artifact.txt").exists()
    assert (run_dir / "logs").exists()
    assert (run_dir / "logs" / "run.log").exists()
