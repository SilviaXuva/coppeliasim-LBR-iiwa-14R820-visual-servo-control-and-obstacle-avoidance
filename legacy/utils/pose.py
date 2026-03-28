import numpy as np
from spatialmath import SE3

class Pose:
    """Pose representation with translation and orientation parameters."""

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        rpy: np.ndarray | None = None,
        r_xyz: np.ndarray | None = None,
    ) -> None:
        """
        Initialize a pose from translation and orientation parameters.

        Parameters
        ----------
        x : float
            Position along the x-axis.
        y : float
            Position along the y-axis.
        z : float
            Position along the z-axis.
        rpy : np.ndarray | None, optional
            Roll-pitch-yaw orientation vector.
        r_xyz : np.ndarray | None, optional
            Sequential rotation angles about x, y, and z axes.
        """
        if rpy is not None and r_xyz is not None:
            raise ValueError("Only one of 'rpy' or 'r_xyz' can be provided.")

        self.x = x
        self.y = y
        self.z = z

        self.rpy = None
        self.r_xyz = None

        if rpy is None and r_xyz is None:
            self.rpy = np.zeros(3)
            self.T = SE3.Trans(self.x, self.y, self.z) * SE3.RPY(self.rpy, order="zyx")

        elif r_xyz is not None:
            self.r_xyz = np.asarray(r_xyz, dtype=float)
            rx, ry, rz = self.r_xyz
            self.T = (
                SE3.Trans(self.x, self.y, self.z)
                * SE3.Rx(rx)
                * SE3.Ry(ry)
                * SE3.Rz(rz)
            )

        else:
            self.rpy = np.asarray(rpy, dtype=float)
            self.T = SE3.Trans(self.x, self.y, self.z) * SE3.RPY(self.rpy, order="zyx")

    def as_se3(self) -> SE3:
        """
        Return the pose as an SE3 object.

        Returns
        -------
        SE3
            Homogeneous transformation.
        """
        return self.T
