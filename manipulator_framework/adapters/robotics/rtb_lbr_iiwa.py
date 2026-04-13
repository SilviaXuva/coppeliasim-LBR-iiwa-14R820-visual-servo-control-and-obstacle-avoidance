import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH


class LBRIiwaRTB(DHRobot):
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

    DEG_TO_RAD = np.pi / 180  # Constant to convert degrees to radians
    MM_TO_M = 1e-3  # Constant to convert millimeters to meters

    def __init__(self):
        """Initialize the LBR iiwa 14R820 robot using standard DH parameters."""
        # Denavit-Hartenberg parameters (d, a, alpha, qlim)
        dh_params = [
            (0.360, 0.0,  90, (-170, 170)),
            (0.000, 0.0, -90, (-120, 120)),
            (0.420, 0.0, -90, (-170, 170)),
            (0.000, 0.0,  90, (-120, 120)),
            (0.400, 0.0,  90, (-170, 170)),
            (0.000, 0.0, -90, (-120, 120)),
            (0.111, 0.0,   0, (-175, 175)),
        ]

        # Dados do Coppelia
        dynamic_params = [
            {
                'm': 2.0,
                'r': [-0.000098,-0.007491,-0.020293],
                'I': [0.061949,0.062637,0.029408,-4e-06,0.007538,3.5e-05]
            },
            {
                'm': 2.0,
                'r': [0.000211,-0.000126,0.005191],
                'I': [0.065481,0.064075,0.027901,-5.5e-05,0.009942,0.000103]
            },
            {
                'm': 2.0,
                'r': [0.000025,0.000143,-0.012514],
                'I': [0.069628,0.066356,0.025493,-1.5e-05,-0.010164,1.7e-05]
            },
            {
                'm': 2.0,
                'r': [-0.000230,-0.002339,0.011745],
                'I': [0.065627,0.06237,0.028491,-3e-06,-0.009585,-1.4e-05]
            },
            {
                'm': 2.0,
                'r': [-0.000162,-0.009587,-0.033274],
                'I': [0.070361,0.065353,0.028704,1.4e-05,0.017439,-2e-06]
            },
            {
                'm': 2.0,
                'r': [-0.000433,-0.002919,0.005707],
                'I': [0.05437,0.05292,0.038595,-1.2e-05,0.002893,-1e-05]
            },
            {
                'm': 1.0,
                'r': [0.000393,-0.000017,-0.002890],
                'I': [0.006603,0.006661,0.011642,1.5e-05,-9e-06,-6e-06]
            }
        ]

        # Create RevoluteDH objects for each joint
        links = [
            RevoluteDH(
                d=d, a=a, alpha=alpha * self.DEG_TO_RAD,
                qlim=[qlim[0] * self.DEG_TO_RAD, qlim[1] * self.DEG_TO_RAD],
                m=params['m'],
                r=params['r'],
                I=params['I'],
                Jm=0.0, B=0.0, Tc=[0.0, 0.0],
                G=1.0
            )
            for (d, a, alpha, qlim), params in zip(dh_params, dynamic_params)
        ]

        # Initialize the robot
        super().__init__(links, name="LBRiiwa14R820", manufacturer="KUKA")

        # Add default configurations
        self._set_default_configurations()

        # Set tool translation
        # self.tool = SE3.Trans(0, 0.119, 0)*SE3.Rx(-90, unit='deg')

        self.tau_max = np.array([176.00, 176.00, 100.00, 100.00, 100.00, 38.00, 38.00])
        self.tau_min = -1 * self.tau_max

        self.gravity = np.array([0, 0, -9.81])

    def _set_default_configurations(self) -> None:
        """Set the default joint configurations for the robot."""
        self.qz = np.zeros(self.n)  # Zero configuration
        self.qr = np.array([0, 0, 0, 90, 0, -90, 90]) * self.DEG_TO_RAD  # Ready configuration
        self.qa = np.array([90, 90, -90, 0, 90, 0, 0]) * self.DEG_TO_RAD

        # Store the forward kinematics of these configurations
        self.Tz = self.fkine(self.qz)
        self.Tr = self.fkine(self.qr)

        # Add configurations for easy access
        self.addconfiguration("qz", self.qz)
        self.addconfiguration("qr", self.qr)
