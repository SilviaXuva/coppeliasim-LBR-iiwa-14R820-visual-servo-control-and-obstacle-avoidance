from __future__ import annotations

from collections.abc import Sequence
from time import time

from coppeliasim_zmqremoteapi_client import RemoteAPIClient

from ...core.models.pose import Pose
from ...core.models.robot_state import RobotState
from ...core.ports.robot_port import RobotPort


class CoppeliaAdapter(RobotPort):
    """Implements RobotPort using CoppeliaSim ZMQ Remote API."""

    def __init__(
        self,
        robot_path: str,
        joints_count: int = 7,
        joints_prefix: str = "./joint",
        tip_path: str | None = "./tip",
        scene_path: str | None = None,
        host: str = "localhost",
        port: int = 23000,
        auto_start: bool = True,
    ) -> None:
        self._client = RemoteAPIClient(host=host, port=port)
        self._sim = self._client.require("sim")

        self._wait_for_stop()
        if scene_path is not None:
            self._sim.loadScene(scene_path)

        self._robot_handle = self._sim.getObject(robot_path)
        self._joints_handles = [
            self._sim.getObject(f"{joints_prefix}{index}") for index in range(joints_count)
        ]

        self._tip_handle: int | None = None
        if tip_path is not None:
            try:
                self._tip_handle = self._sim.getObject(tip_path)
            except Exception:
                self._tip_handle = None

        if auto_start:
            self.start()

    @property
    def sim(self) -> object:
        return self._sim

    def start(self) -> None:
        self._sim.setStepping(True)
        self._sim.startSimulation()
        self._client.step()

    def stop(self) -> None:
        self._sim.stopSimulation()
        self._wait_for_stop()
        try:
            self._sim.setStepping(False)
        except Exception:
            pass

    def get_state(self) -> RobotState:
        joints_positions = self.get_joints_positions()
        joints_velocities = self._get_joints_velocities()
        tool_pose = self._get_tool_pose()
        return RobotState(
            joints_positions=joints_positions,
            joints_velocities=joints_velocities,
            tool_pose=tool_pose,
            timestamp_s=time(),
        )

    def get_joints_positions(self) -> tuple[float, ...]:
        return tuple(
            float(self._sim.getJointPosition(joints_handles))
            for joints_handles in self._joints_handles
        )

    def command_joints_positions(self, joints_positions: Sequence[float]) -> None:
        self._validate_size(joints_positions)
        for joints_handles, position in zip(self._joints_handles, joints_positions):
            self._sim.setJointTargetPosition(joints_handles, float(position))

    def command_joints_velocities(self, joints_velocities: Sequence[float]) -> None:
        self._validate_size(joints_velocities)
        for joints_handles, velocity in zip(self._joints_handles, joints_velocities):
            self._sim.setJointTargetVelocity(joints_handles, float(velocity))

    def step(self, reference_xyz: Sequence[float] | None = None) -> None:
        del reference_xyz
        self._client.step()

    def _wait_for_stop(self, max_steps: int = 500) -> None:
        for _ in range(max_steps):
            if self._sim.getSimulationState() == self._sim.simulation_stopped:
                return
            self._sim.stopSimulation()
            try:
                self._client.step()
            except Exception:
                pass

    def _validate_size(self, values: Sequence[float]) -> None:
        if len(values) != len(self._joints_handles):
            raise ValueError(
                f"Expected {len(self._joints_handles)} values, got {len(values)}."
            )

    def _get_joints_velocities(self) -> tuple[float, ...]:
        velocities: list[float] = []
        for joints_handles in self._joints_handles:
            try:
                velocity = self._sim.getObjectFloatParam(
                    joints_handles, self._sim.jointfloatparam_velocity
                )
            except Exception:
                velocity = 0.0
            velocities.append(float(velocity))
        return tuple(velocities)

    def _get_tool_pose(self) -> Pose | None:
        if self._tip_handle is None:
            return None
        try:
            position = self._sim.getObjectPosition(self._tip_handle, self._sim.handle_world)
            alpha_beta_gamma = self._sim.getObjectOrientation(
                self._tip_handle, self._sim.handle_world
            )
            yaw, pitch, roll = self._sim.alphaBetaGammaToYawPitchRoll(
                alpha_beta_gamma[0],
                alpha_beta_gamma[1],
                alpha_beta_gamma[2],
            )
            return Pose(
                x=float(position[0]),
                y=float(position[1]),
                z=float(position[2]),
                roll=float(roll),
                pitch=float(pitch),
                yaw=float(yaw),
            )
        except Exception:
            return None
