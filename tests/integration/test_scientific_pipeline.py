from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from manipulator_framework.adapters.stubs import StubMarkerDetector, StubPoseEstimator
from manipulator_framework.application.composition.simulation_composer import SimulationComposer
from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from manipulator_framework.core.types import (
    JointState,
    Pose3D,
    RobotState,
)


class _FakeSimClient:
    def __init__(self) -> None:
        self._sim_time = 0.0

    def start_simulation(self) -> None:
        return None

    def step_simulation(self) -> None:
        self._sim_time += 0.1

    def stop_simulation(self) -> None:
        return None

    def get_joint_position(self, *, robot_handle: Any, joint_name: str) -> float:
        return 0.0

    def get_joint_velocity(self, *, robot_handle: Any, joint_name: str) -> float:
        return 0.0

    def set_joint_target_position(self, *, robot_handle: Any, joint_name: str, value: float) -> None:
        return None

    def set_joint_torque(self, *, robot_handle: Any, joint_name: str, value: float) -> None:
        return None

    def get_object_position(self, *, handle: Any, reference_frame: str = "world") -> list[float]:
        return [0.5, 0.0, 0.6]

    def get_object_quaternion(self, *, handle: Any, reference_frame: str = "world") -> list[float]:
        return [0.0, 0.0, 0.0, 1.0]

    def get_sim_time(self) -> float:
        return self._sim_time

    def get_camera_rgb(self, *, camera_handle: Any) -> np.ndarray:
        return np.zeros((32, 32, 3), dtype=np.uint8)

    def get_camera_intrinsics(self, *, camera_handle: Any) -> np.ndarray:
        return np.eye(3, dtype=float)


class _FakeYoloModel:
    def predict(self, image, conf: float = 0.5, verbose: bool = False):
        return []


@pytest.fixture
def temp_results_dir():
    """Temporary directory for experiment runs during testing."""
    path = Path(tempfile.gettempdir()) / "framework_integration_tests"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def test_scientific_pipeline_integration_full_path(temp_results_dir: Path) -> None:
    """
    INTEGRATION TEST (5.1 & 5.2): 
    Validates the end-to-end flow from Use Case to Repository and scientific consistency.
    """
    # 1. Setup Configuration
    config = {
        "experiment": {"name": "integration_test", "seed": 999, "tags": ["test"]},
        "planning": {"duration": 0.2, "dt": 0.1}, # 2 cycles
        "results": {"base_dir": str(temp_results_dir)},
        "simulation": {"use_camera": True}
    }

    # 2. Composition (Mocking sim_client to avoid remote ZMQ dependencies)
    composer = SimulationComposer(
        config=config,
        sim_client=_FakeSimClient(),
        yolo_model=_FakeYoloModel(),
    )
    
    # 3. Get the Thick Use Case
    use_case = composer.build_run_pbvs_with_avoidance()
    
    # 4. Override dependencies to make this integration test deterministic.
    use_case.robot = _create_mock_robot()
    use_case.camera = _create_mock_camera()
    use_case.marker_detector = StubMarkerDetector()
    use_case.pose_estimator = StubPoseEstimator()
    
    # 5. Create the Request
    request = RunPBVSWithAvoidanceRequest(
        run_id="test_run_001",
        config=config,
        seed=999,
        duration=0.2,
        max_cycles=2
    )

    # 6. EXECUTION (The CORE of the test)
    response = use_case.execute(request)

    # 7. VALIDATION (5.1 Integration)
    assert response.run_result.success is True
    assert len(response.cycle_results) == 2
    
    # Check Persistence (Entrega 4 traceability)
    run_path = temp_results_dir / "test_run_001"
    assert (run_path / "summary.json").exists()
    assert (run_path / "metadata.json").exists()
    assert (run_path / "config.yaml").exists()
    assert (run_path / "logs" / "run.log").exists()

    # 8. SCIENTIFIC VALIDATION (5.2 Regression)
    # Check that cycles have timestamps and canonical cycle events
    final_cycle = response.cycle_result
    assert final_cycle.cycle_index == 1
    assert final_cycle.timestamp > 0
    assert len(final_cycle.events) > 0


def _create_mock_robot():
    from unittest.mock import MagicMock
    robot = MagicMock()
    robot.get_robot_state.return_value = RobotState(
        joint_state=JointState(
            np.zeros(7),
            np.zeros(7),
            joint_names=tuple(f"j{i}" for i in range(7)),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(np.array([0.5, 0, 0.7]), np.array([0, 0, 0, 1])),
        timestamp=0.0
    )
    return robot


def _create_mock_camera():
    from unittest.mock import MagicMock
    camera = MagicMock()
    camera.get_frame.return_value = MagicMock() # CameraFrame
    return camera
