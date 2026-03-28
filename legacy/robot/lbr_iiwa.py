import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3

from utils import DEG_TO_RAD

class LBR_iiwa_DH(DHRobot):
    """
    Class that models a KUKA LBR iiwa 14R820 manipulator using Denavit-Hartenberg parameters.

    This class defines the kinematic characteristics of the LBR iiwa 14R820 collaborative robot,
    including standard configurations such as 'zero' (qz) and 'ready' (qr).

    Attributes:
        qr (np.ndarray): Ready configuration of the manipulator.
        qz (np.ndarray): Zero configuration of the manipulator.

    Methods:
        fkine(q): Compute the forward kinematics for a given joint configuration `q`.
    """

    def __init__(self) -> None:
        """Initialize the KUKA LBR iiwa 14R820 robot model."""
        name = "LBRiiwa14R820"

        dh_params = [
            (0.360, 0.0, 90, (-170, 170)),
            (0.000, 0.0, -90, (-120, 120)),
            (0.420, 0.0, -90, (-170, 170)),
            (0.000, 0.0, 90, (-120, 120)),
            (0.400, 0.0, 90, (-170, 170)),
            (0.000, 0.0, -90, (-120, 120)),
            (0.230, 0.0, 0, (-175, 175)),
        ]

        dynamic_params = [
            {
                "m": 2.0,
                "r": [-0.000098, -0.007491, -0.020293],
                "I": [0.061949, 0.062637, 0.029408, -4e-06, 0.007538, 3.5e-05],
            },
            {
                "m": 2.0,
                "r": [0.000211, -0.000126, 0.005191],
                "I": [0.065481, 0.064075, 0.027901, -5.5e-05, 0.009942, 0.000103],
            },
            {
                "m": 2.0,
                "r": [0.000025, 0.000143, -0.012514],
                "I": [0.069628, 0.066356, 0.025493, -1.5e-05, -0.010164, 1.7e-05],
            },
            {
                "m": 2.0,
                "r": [-0.000230, -0.002339, 0.011745],
                "I": [0.065627, 0.06237, 0.028491, -3e-06, -0.009585, -1.4e-05],
            },
            {
                "m": 2.0,
                "r": [-0.000162, -0.009587, -0.033274],
                "I": [0.070361, 0.065353, 0.028704, 1.4e-05, 0.017439, -2e-06],
            },
            {
                "m": 2.0,
                "r": [-0.000433, -0.002919, 0.005707],
                "I": [0.05437, 0.05292, 0.038595, -1.2e-05, 0.002893, -1e-05],
            },
            {
                "m": 1.0,
                "r": [0.000393, -0.000017, -0.002890],
                "I": [0.006603, 0.006661, 0.011642, 1.5e-05, -9e-06, -6e-06],
            },
        ]

        links = [
            RevoluteDH(
                d=d,
                a=a,
                alpha=alpha * DEG_TO_RAD,
                qlim=[qlim[0] * DEG_TO_RAD, qlim[1] * DEG_TO_RAD],
                m=params["m"],
                r=params["r"],
                I=params["I"],
                Jm=0.0,
                B=0.0,
                Tc=[0.0, 0.0],
                G=1.0,
            )
            for (d, a, alpha, qlim), params in zip(dh_params, dynamic_params)
        ]

        super().__init__(links, name=name, manufacturer="KUKA")

        # self.tool = SE3.Trans(0, 0, 0.119)  # Tool frame offset along z-axis

        self._set_default_configurations()

    def _set_default_configurations(self) -> None:
        """Set default joint configurations and model torque limits."""
        self.qz = np.zeros(self.n)
        self.qr = np.array([0, 0, 0, 90, 0, -90, 90]) * DEG_TO_RAD

        self.tau = np.zeros(self.n)
        self.tau_max = np.array([176.0, 176.0, 100.0, 100.0, 100.0, 38.0, 38.0])
        self.tau_min = -self.tau_max

        self.Tz = self.fkine(self.qz)
        self.Tr = self.fkine(self.qr)

        self.addconfiguration("qz", self.qz)
        self.addconfiguration("qr", self.qr)

    def step(self) -> None:
        """No per-step update is required for the kinematic robot model."""
        return None
