import logging
from roboticstoolbox.backends.PyPlot import PyPlot

from sim.pyplot.sim_object import SimObject
from sim.pyplot.external_object import ExternalObject
from utils import MS_TO_S

logger = logging.getLogger("PyPlot")

class PyPlot(PyPlot):
    """Main interface for managing a PyPlot simulation session."""

    class ObjectsContainer:
        """Container for simulation objects."""
        pass

    class ExternalObjectsContainer:
        """Container for external processing objects."""
        pass

    def __init__(
        self,
        ts: float = 50 * MS_TO_S,
    ) -> None:
        """
        Initialize the PyPlot session.

        Parameters
        ----------
        stepping : bool, optional
            Whether stepped simulation mode should be enabled.
        scene : str, optional
            Scene filename to be loaded.
        ts : float, optional
            Simulation step time.
        dyn_ts : float, optional
            Dynamics step time.
        """
        self.sim_name = "PyPlot"
        self.started = False

        super().__init__()
        self.ts = ts


        self.objects = self.ObjectsContainer()
        self.external_objects = self.ExternalObjectsContainer()

    def get_sim_time(self) -> None:
        """Get simulation time"""
        return self.sim_time - self.ts
    
    def add_object(self, obj: SimObject) -> None:
        """
        Register a simulation object.

        Parameters
        ----------
        obj : SimObject
            Object to be added to the simulation object container.
        """
        self.add(obj)
        setattr(self.objects, obj.obj_name, obj)

    def add_external_object(self, obj: ExternalObject) -> None:
        """
        Register an external processing object.

        Parameters
        ----------
        obj : ExternalObject
            Object to be added to the external object container.
        """
        setattr(self.external_objects, obj.obj_name, obj)

    def start(self) -> None:
        """Start the simulation."""
        if self.started:
            logger.warning("%s simulation already started", self.sim_name)
            return

        logger.info("Starting %s simulation", self.sim_name)
        self.launch()

        self.started = True
        logger.info("%s simulation started", self.sim_name)

    def stop(self) -> None:
        """Stop the simulation and release object resources."""
        logger.info("Stopping %s simulation", self.sim_name)

        if hasattr(self, "objects"):
            for obj in self.objects.__dict__.values():
                if hasattr(obj, "stop"):
                    obj.stop()

        super().close()

        self.started = False
        logger.info("%s simulation stopped", self.sim_name)

    def step(self) -> None:
        """Advance one application-level simulation step."""
        for obj in self.objects.__dict__.values():
            if hasattr(obj, "step"):
                obj.step()

        for obj_name, obj in self.external_objects.__dict__.items():
            if not hasattr(obj, "step"):
                continue

            if obj_name == "ArUcoDetector":
                if hasattr(self.objects, "VisionSensor"):
                    vs = getattr(self.objects, "VisionSensor")
                elif hasattr(self.objects, "VisionDepthSensor"):
                    vs = getattr(self.objects, "VisionDepthSensor")
                else:
                    raise RuntimeError(
                        "ArUcoDetector requires at least one vision sensor (RGB or RGB-D)."
                    )

                obj.step(
                    self.sim,
                    vs.rgb_sensor_path,
                    vs.frame,
                    vs.intrinsic_matrix,
                    vs.T_vs2w,
                    vs.distortion_coefficients,
                )

            elif obj_name == "YoloDetector":
                if hasattr(self.objects, "VisionDepthSensor"):
                    vs = getattr(self.objects, "VisionDepthSensor")
                else:
                    raise RuntimeError("YoloDetector requires an RGB-D camera.")

                obj.step(
                    self.sim,
                    vs.frame,
                    vs.depth,
                    vs.fx,
                    vs.fy,
                    vs.cx,
                    vs.cy,
                    vs.R_w2vs,
                    vs.t_w2vs,
                )

            else:
                obj.step()
    
        super().step(self.ts)
