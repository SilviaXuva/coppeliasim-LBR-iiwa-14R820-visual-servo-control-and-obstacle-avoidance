import logging
import time

import numpy as np

from sim.coppelia_sim.sim_object import SimObject

logger = logging.getLogger("Trajectory Drawing")

class TrajDrawing(SimObject):
    """Draw current and reference trajectories in CoppeliaSim."""

    tip_path = "./tip"

    class Drawing:
        """Helper class for drawing line segments in CoppeliaSim."""

        cyclic = 500  # Maximum number of stored line segments

        def __init__(self, sim, tip_handle: int, color: list[float]) -> None:
            """
            Initialize a drawing object.

            Parameters
            ----------
            sim : object
                CoppeliaSim simulation interface.
            tip_handle : int
                Handle of the tracked object.
            color : list[float]
                RGB color of the trajectory.
            """
            self.sim = sim
            self.tip_handle = tip_handle
            self.obj = self.sim.addDrawingObject(
                self.sim.drawing_lines | self.sim.drawing_cyclic,
                2,
                0,
                -1,
                self.cyclic,
                color,
            )
            self.pos = np.array(
                self.sim.getObjectPosition(self.tip_handle, self.sim.handle_world)
            )

        def update_line(self, pos) -> None:
            """
            Append a new line segment from the previous position to the given position.

            Parameters
            ----------
            pos : array-like
                Current position of the tracked point.
            """
            pos = np.array(pos)
            line = np.concatenate([self.pos, pos])
            self.sim.addDrawingObjectItem(self.obj, line.tolist())
            self.pos = pos

        def clear(self) -> None:
            """Remove this drawing object from the simulation."""
            try:
                self.sim.addDrawingObjectItem(self.obj, None)
                self.sim.removeDrawingObject(self.obj)
            except Exception:
                pass

    class RefTraj(Drawing):
        """Reference trajectory drawing."""

        def __init__(self, sim, tip_handle: int, color: list[float] = [0, 0, 1]) -> None:
            """Initialize the reference trajectory drawing."""
            super().__init__(sim, tip_handle, color)

    class CurrentTraj(Drawing):
        """Current trajectory drawing."""

        def __init__(self, sim, tip_handle: int, color: list[float] = [1, 0, 0]) -> None:
            """Initialize the current trajectory drawing."""
            super().__init__(sim, tip_handle, color)

        def update_from_tip(self) -> None:
            """Update the trajectory using the current tip world position."""
            pos = self.sim.getObjectPosition(self.tip_handle, self.sim.handle_world)
            super().update_line(pos)

    def __init__(self, sim) -> None:
        """
        Initialize trajectory drawing objects.

        Parameters
        ----------
        sim : object
            CoppeliaSim simulation interface.
        """
        super().__init__(
            obj_name="Drawing",
            client=None,
            sim=sim,
            is_thread=True,
        )

        self.tip_handle = self.sim.getObject(self.tip_path)
        self.ref_traj = self.RefTraj(self.sim, self.tip_handle)
        self.current_traj = self.CurrentTraj(self.sim, self.tip_handle)

        self.ref_pos = None
        self._running = True

        self.start()

    def run(self) -> None:
        """Continuously update trajectory drawings in the background."""
        while self._running:
            try:
                self.current_traj.update_from_tip()

                if self.ref_pos is not None:
                    self.ref_traj.update_line(self.ref_pos)

                self.event.set()
                time.sleep(0.001)
                
            except Exception:
                logger.exception("Error while updating trajectory drawing.")
                time.sleep(0.01)

    def step(self) -> None:
        """Wait for one drawing update cycle."""
        self.event.wait()
        self.event.clear()

    def stop(self) -> None:
        """Stop the drawing thread and remove created drawing objects."""
        logger.info("Stopping trajectory drawing...")

        self._running = False

        self.current_traj.clear()
        self.ref_traj.clear()

def clear_all_drawings(sim, max_handle: int = 5) -> None:
    """
    Remove drawing objects that may still exist in the current simulation.

    Parameters
    ----------
    sim : object
        CoppeliaSim simulation interface.
    max_handle : int, optional
        Maximum drawing handle value to probe during cleanup.
    """
    logger.info("Clearing drawing objects...")

    for handle in range(1, max_handle + 1):
        try:
            sim.addDrawingObjectItem(handle, None)
            sim.removeDrawingObject(handle)
        except Exception:
            continue
