import cv2
import logging
import numpy as np
from spatialmath import SE3

from sim.coppelia_sim.sim_object import SimObject
from utils import fmt_array
from vision.gui import show_img

logger = logging.getLogger("Vision Sensor")

class VisionSensor(SimObject):
    """Interface for an RGB vision sensor in CoppeliaSim."""

    def __init__(
        self,
        sim,
        sensor_path: str = "./rgb",
        obj_name: str = "VisionSensor",
        distortion_coefficients=None,
    ) -> None:
        """
        Initialize the vision sensor.

        Parameters
        ----------
        sim : object
            CoppeliaSim simulation interface.
        sensor_path : str, optional
            Path of the RGB sensor in CoppeliaSim.
        obj_name : str, optional
            Simulation object name.
        distortion_coefficients : array-like | None, optional
            Distortion coefficients of the camera model. Use None for an ideal sensor.
        """
        super().__init__(
            obj_name=obj_name,
            client=None,
            sim=sim,
            is_thread=False,
        )

        self.rgb_sensor_path = sensor_path
        self.handle = self.sim.getObject(self.rgb_sensor_path)
        self.distortion_coefficients = distortion_coefficients

        self.get_parameters()
        self.get_intrinsic_matrix()
        self.get_extrinsic_matrix()
        self.get_img()

    def get_parameters(self) -> None:
        """Read sensor resolution and field-of-view parameters."""
        self.res_x, self.res_y = self.sim.getVisionSensorRes(self.handle)
        self.perspective_angle = self.sim.getObjectFloatParam(
            self.handle,
            self.sim.visionfloatparam_perspective_angle,
        )

        aspect_ratio = self.res_x / self.res_y
        self.fov_y = self.perspective_angle
        self.fov_x = 2 * np.arctan(np.tan(self.fov_y / 2) * aspect_ratio)

    def get_intrinsic_matrix(self) -> None:
        """Compute the camera intrinsic matrix."""
        self.cx = self.res_x / 2
        self.cy = self.res_y / 2

        self.fx = self.cx / np.tan(self.fov_x / 2)
        self.fy = self.cy / np.tan(self.fov_y / 2)

        self.intrinsic_matrix = np.array(
            [
                [self.fx, 0, self.cx],
                [0, self.fy, self.cy],
                [0, 0, 1],
            ]
        )
        self.K = self.intrinsic_matrix

        logger.debug("Vision sensor intrinsic matrix:\n%s", fmt_array(self.intrinsic_matrix))
        logger.debug("Distortion coefficients:\n%s", fmt_array(self.distortion_coefficients))

    def get_extrinsic_matrix(self) -> None:
        """Compute the sensor pose and extrinsic parameters with respect to the world frame."""
        pos = self.sim.getObjectPosition(self.handle, self.sim.handle_world)
        abg = self.sim.getObjectOrientation(self.handle, self.sim.handle_world)
        ypr = self.sim.alphaBetaGammaToYawPitchRoll(abg[0], abg[1], abg[2])
        rpy = [ypr[2], ypr[1], ypr[0]]

        self.T_vs2w = (SE3.Trans(pos) * SE3.RPY(rpy, order="zyx")).A

        self.R_vs2w = self.T_vs2w[:3, :3]
        self.t_vs2w = self.T_vs2w[:3, 3]

        self.R_w2vs = self.R_vs2w.T
        self.t_w2vs = -self.R_w2vs @ self.t_vs2w

        logger.debug("Vision sensor extrinsic matrix:\n%s", fmt_array(self.T_vs2w))

    def get_img(self) -> None:
        """Capture the current RGB frame from the vision sensor."""
        self.sim.handleVisionSensor(self.handle)
        frame_bytes, (res_x, res_y) = self.sim.getVisionSensorImg(self.handle)

        expected_size = res_x * res_y * 3
        if len(frame_bytes) != expected_size:
            raise ValueError(
                f"Unexpected image buffer size: got {len(frame_bytes)}, "
                f"expected {expected_size}."
            )

        frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(res_y, res_x, 3)
        self.frame = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 0)

    def step(self) -> None:
        """Update the current RGB frame."""
        self.get_img()

    def show(self, window_name: str = "Original Flipped Frame") -> None:
        """
        Display the current RGB frame.

        Parameters
        ----------
        window_name : str, optional
            Window title.
        """
        show_img(window_name, self.frame)

    def stop(self) -> None:
        """Close all OpenCV windows related to the vision sensor."""
        logger.info("Closing all windows...")
        cv2.destroyAllWindows()
