import logging
from pathlib import Path

from coppeliasim_zmqremoteapi_client import RemoteAPIClient

from sim.coppelia_sim.sim_object import SimObject
from sim.coppelia_sim.external_object import ExternalObject
from sim.coppelia_sim.objects.traj_drawing import clear_all_drawings
from utils import MS_TO_S

logger = logging.getLogger("CoppeliaSim")

root_dir = Path(__file__).resolve().parent.parent.parent
scenes_path = (root_dir.parent / "scenes").resolve()

class CoppeliaSim:
    """Main interface for managing a CoppeliaSim simulation session."""

    class ObjectsContainer:
        """Container for simulation objects."""
        pass

    class ExternalObjectsContainer:
        """Container for external processing objects."""
        pass

    def __init__(
        self,
        stepping: bool = False,
        scene: str = "1.ttt",
        ts: float = 50 * MS_TO_S,
        dyn_ts: float = 5 * MS_TO_S,
    ) -> None:
        """
        Initialize the CoppeliaSim session.

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
        self.sim_name = "CoppeliaSim"
        self.stepping = stepping
        self.started = False

        logger.info("Connecting to CoppeliaSim RemoteAPI...")
        self.client = RemoteAPIClient()
        self.sim = self.client.require("sim")
        logger.info("RemoteAPI connected")

        while self.sim.getSimulationState() != self.sim.simulation_stopped:
            self.stop()

        scene_path = scenes_path / scene
        logger.info("Loading scene '%s'", scene_path)

        try:
            self.sim.loadScene(str(scene_path))
            logger.info("Scene loaded successfully")
        except Exception:
            logger.exception("Failed to load scene '%s'", scene_path)
            raise

        logger.info("Changing scene properties...")
        self.sim.setBoolProperty(self.sim.handle_scene, "dynamicsEnabled", True)
        self.sim.setIntArrayProperty(
            self.sim.handle_scene,
            "dynamicsEngine",
            [self.sim.physics_newton, 0],
        )
        self.sim.setBoolProperty(
            self.sim.handle_scene,
            "newton.computeInertias",
            False,
        )
        self.sim.setFloatProperty(self.sim.handle_scene, "timeStep", ts)
        self.sim.setFloatProperty(self.sim.handle_scene, "dynamicsStepSize", dyn_ts)

        self.objects = self.ObjectsContainer()
        self.external_objects = self.ExternalObjectsContainer()

    def add_object(self, obj: SimObject) -> None:
        """
        Register a simulation object.

        Parameters
        ----------
        obj : SimObject
            Object to be added to the simulation object container.
        """
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

        logger.info("Starting %s simulation (stepping=%s)", self.sim_name, self.stepping)

        self.sim.setInt32Param(self.sim.intparam_idle_fps, 0)
        self.sim.setStepping(self.stepping)
        self.sim.startSimulation()

        self.started = True
        logger.info("%s simulation started", self.sim_name)

    def stop(self) -> None:
        """Stop the simulation and release object resources."""
        logger.info("Stopping %s simulation", self.sim_name)

        if hasattr(self, "objects"):
            for obj in self.objects.__dict__.values():
                if hasattr(obj, "stop"):
                    obj.stop()

        self.sim.stopSimulation()
        clear_all_drawings(self.sim)
        
        self.sim.setInt32Param(self.sim.intparam_idle_fps, 8)

        self.started = False
        sim_time = self.sim.getSimulationTime()
        logger.info("%s simulation stopped at t=%.2fs", self.sim_name, sim_time)

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

        if self.stepping:
            self.client.step()
