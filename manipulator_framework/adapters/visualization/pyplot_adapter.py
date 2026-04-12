from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt

from ...core.models.marker_state import MarkerState
from ...core.models.person_state import PersonState
from ...core.models.pose import Pose
from ...core.models.robot_state import RobotState
from ...core.ports.visualization_port import VisualizationPort


class PyPlotAdapter(VisualizationPort):
    """Implements VisualizationPort using Matplotlib PyPlot."""

    def __init__(self) -> None:
        plt.ion()
        self._figure = plt.figure("Manipulator Framework")
        self._axis = self._figure.add_subplot(111, projection="3d")

        self._tool_path: list[tuple[float, float, float]] = []
        self._reference_path: tuple[Pose, ...] = ()
        self._markers: tuple[MarkerState, ...] = ()
        self._people: tuple[PersonState, ...] = ()
        self._configure_axes()

    def update_robot_state(self, state: RobotState) -> None:
        if state.tool_pose is not None:
            self._tool_path.append(state.tool_pose.xyz)
        self._redraw()

    def update_reference_path(self, reference_path: Sequence[Pose]) -> None:
        self._reference_path = tuple(reference_path)
        self._redraw()

    def update_markers(self, markers: Sequence[MarkerState]) -> None:
        self._markers = tuple(markers)
        self._redraw()

    def update_people(self, people: Sequence[PersonState]) -> None:
        self._people = tuple(people)
        self._redraw()

    def clear(self) -> None:
        self._tool_path.clear()
        self._reference_path = ()
        self._markers = ()
        self._people = ()
        self._redraw()

    def _configure_axes(self) -> None:
        self._axis.set_xlabel("X (m)")
        self._axis.set_ylabel("Y (m)")
        self._axis.set_zlabel("Z (m)")
        self._axis.set_title("Robot / Reference / Perception")

    def _redraw(self) -> None:
        self._axis.cla()
        self._configure_axes()

        if len(self._reference_path) > 0:
            ref_x = [pose.x for pose in self._reference_path]
            ref_y = [pose.y for pose in self._reference_path]
            ref_z = [pose.z for pose in self._reference_path]
            self._axis.plot(ref_x, ref_y, ref_z, linestyle="--", label="reference")

        if len(self._tool_path) > 0:
            tool_x, tool_y, tool_z = zip(*self._tool_path)
            self._axis.plot(tool_x, tool_y, tool_z, label="tool_path")
            self._axis.scatter(tool_x[-1], tool_y[-1], tool_z[-1], marker="o")

        for marker in self._markers:
            if marker.pose_world is None:
                continue
            color = marker.color if marker.color is not None else "tab:orange"
            self._axis.scatter(
                marker.pose_world.x,
                marker.pose_world.y,
                marker.pose_world.z,
                color=color,
                marker="s",
            )
            self._axis.text(
                marker.pose_world.x,
                marker.pose_world.y,
                marker.pose_world.z,
                f"m{marker.marker_id}",
            )

        for person in self._people:
            if person.pose_world is None:
                continue
            self._axis.scatter(
                person.pose_world.x,
                person.pose_world.y,
                person.pose_world.z,
                color="tab:red",
                marker="^",
            )
            self._axis.text(
                person.pose_world.x,
                person.pose_world.y,
                person.pose_world.z,
                person.person_id,
            )

        self._axis.legend(loc="upper right")
        self._figure.canvas.draw_idle()
        self._figure.canvas.flush_events()
        plt.pause(0.001)
