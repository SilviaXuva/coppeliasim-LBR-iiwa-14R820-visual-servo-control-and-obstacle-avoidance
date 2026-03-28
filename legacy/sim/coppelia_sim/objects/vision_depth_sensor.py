import logging
import numpy as np

from sim.coppelia_sim.objects.vision_sensor import VisionSensor
from vision.gui import show_img

logger = logging.getLogger("Vision Depth Sensor")

class VisionDepthSensor(VisionSensor):
    """Interface for an RGB-D vision sensor in CoppeliaSim."""

    def __init__(
        self,
        sim,
        rgb_sensor_path: str = "./kinect/joint/rgb",
        depth_sensor_path: str = "./kinect/joint/depth",
    ) -> None:
        """
        Initialize the RGB-D vision sensor.

        Parameters
        ----------
        sim : object
            CoppeliaSim simulation interface.
        rgb_sensor_path : str, optional
            Path of the RGB sensor in CoppeliaSim.
        depth_sensor_path : str, optional
            Path of the depth sensor in CoppeliaSim.
        """
        super().__init__(
            sim=sim,
            sensor_path=rgb_sensor_path,
            obj_name="VisionDepthSensor",
        )

        self.depth_sensor_path = depth_sensor_path
        self.depth_sensor_handle = self.sim.getObject(self.depth_sensor_path)

        self.get_depth()

    def get_depth(self) -> None:
        """Capture the current depth frame from the depth sensor."""
        self.sim.handleVisionSensor(self.depth_sensor_handle)
        depth_bytes, (res_x, res_y) = self.sim.getVisionSensorDepth(
            self.depth_sensor_handle,
            1,
        )

        expected_size = res_x * res_y
        depth = np.frombuffer(depth_bytes, dtype=np.float32)

        if depth.size != expected_size:
            raise ValueError(
                f"Unexpected depth buffer size: got {depth.size}, "
                f"expected {expected_size}."
            )

        self.depth = np.flipud(depth.reshape(res_y, res_x))

    def step(self) -> None:
        """Update the current RGB and depth frames."""
        self.get_img()
        self.get_depth()

    def show(self, window_name: str = "Original Flipped Frame") -> None:
        """
        Display the current RGB frame.

        Parameters
        ----------
        window_name : str, optional
            Window title.
        """
        show_img(window_name, self.frame)

    def show_depth(self, window_name: str = "Depth Frame") -> None:
        """
        Display the current depth frame.

        Parameters
        ----------
        window_name : str, optional
            Window title.
        """
        show_img(window_name, self.depth)
