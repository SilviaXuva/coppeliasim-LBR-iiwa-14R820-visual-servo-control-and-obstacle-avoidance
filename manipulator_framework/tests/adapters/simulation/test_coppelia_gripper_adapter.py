import unittest

from manipulator_framework.adapters.simulation.coppelia_gripper_adapter import (
    CoppeliaGripperAdapter,
)


class _FakeSim:
    handle_all = -2

    def __init__(self) -> None:
        self._handles_by_path: dict[str, int] = {}
        self._next_handle = 1
        self.joints_positions: dict[int, float] = {}
        self.joints_target_positions: dict[int, float] = {}
        self.step_calls = 0
        self.proximity_by_sensor: dict[int, tuple[int, float]] = {}

    def getObject(self, path: str) -> int:
        if path not in self._handles_by_path:
            self._handles_by_path[path] = self._next_handle
            self._next_handle += 1
        handle = self._handles_by_path[path]
        self.joints_positions.setdefault(handle, 0.0)
        self.joints_target_positions.setdefault(handle, 0.0)
        return handle

    def setJointTargetPosition(self, joint_handle: int, position: float) -> None:
        self.joints_target_positions[joint_handle] = float(position)

    def getJointPosition(self, joint_handle: int) -> float:
        return self.joints_positions[joint_handle]

    def checkProximitySensor(self, sensor_handle: int, target_handle: int):
        del target_handle
        return self.proximity_by_sensor.get(sensor_handle, (0, 1.0))

    def stepPhysics(self) -> None:
        self.step_calls += 1
        for handle, current in list(self.joints_positions.items()):
            target = self.joints_target_positions.get(handle, current)
            delta = target - current
            if abs(delta) <= 0.05:
                self.joints_positions[handle] = target
            elif delta > 0.0:
                self.joints_positions[handle] = current + 0.05
            else:
                self.joints_positions[handle] = current - 0.05


class TestCoppeliaGripperAdapter(unittest.TestCase):
    def test_init_rejects_empty_joints_paths(self) -> None:
        sim = _FakeSim()
        with self.assertRaises(ValueError):
            CoppeliaGripperAdapter(sim=sim, joints_paths=())

    def test_grasp_waits_for_settle_steps_without_sensor(self) -> None:
        sim = _FakeSim()
        joint_handle = sim.getObject("./active1")
        sim.joints_positions[joint_handle] = 0.20

        adapter = CoppeliaGripperAdapter(
            sim=sim,
            joints_paths=("./active1",),
            open_joints_positions=0.2,
            closed_joints_positions=0.0,
            joints_positions_tolerance=1e-6,
            settle_steps=5,
            step_callback=sim.stepPhysics,
        )

        grasped = adapter.grasp()

        self.assertTrue(grasped)
        self.assertGreater(sim.step_calls, 0)
        self.assertAlmostEqual(sim.joints_positions[joint_handle], 0.0, places=8)

    def test_grasp_uses_proximity_sensor_when_configured(self) -> None:
        sim = _FakeSim()
        sensor_handle = sim.getObject("./attachProxSensor")
        sim.proximity_by_sensor[sensor_handle] = (1, 0.005)

        adapter = CoppeliaGripperAdapter(
            sim=sim,
            joints_paths=("./active1",),
            proximity_sensor_path="./attachProxSensor",
            proximity_distance_threshold=0.01,
            settle_steps=1,
            step_callback=sim.stepPhysics,
        )

        self.assertTrue(adapter.grasp())

        sim.proximity_by_sensor[sensor_handle] = (0, 1.0)
        self.assertFalse(adapter.grasp())


if __name__ == "__main__":
    unittest.main()
