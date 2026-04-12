import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH


class LBRIiwaRTB(DHRobot):
    """Modelo DH do Kuka LBR iiwa 14 R820 usando Robotics Toolbox."""

    def __init__(self) -> None:
        deg = np.pi / 180.0
        mm = 1e-3
        flange = 230 * mm

        links = [
            RevoluteDH(d=0.360, a=0.0, alpha=90 * deg, qlim=[-170 * deg, 170 * deg]),
            RevoluteDH(d=0.000, a=0.0, alpha=-90 * deg, qlim=[-120 * deg, 120 * deg]),
            RevoluteDH(d=0.420, a=0.0, alpha=-90 * deg, qlim=[-170 * deg, 170 * deg]),
            RevoluteDH(d=0.000, a=0.0, alpha=90 * deg, qlim=[-120 * deg, 120 * deg]),
            RevoluteDH(d=0.400, a=0.0, alpha=90 * deg, qlim=[-170 * deg, 170 * deg]),
            RevoluteDH(d=0.000, a=0.0, alpha=-90 * deg, qlim=[-120 * deg, 120 * deg]),
            RevoluteDH(d=flange, a=0.0, alpha=0.0, qlim=[-175 * deg, 175 * deg]),
        ]

        super().__init__(links, name="LBRiiwa14R820", manufacturer="Kuka")

        self.qr = np.array([0, 0, 0, 90 * deg, 0, -90 * deg, 90 * deg], dtype=float)
        self.qz = np.zeros(self.n, dtype=float)

        self.Tr = self.fkine(self.qr)
        self.Tz = self.fkine(self.qz)

        self.addconfiguration("qr", self.qr)
        self.addconfiguration("qz", self.qz)

        self.q = self.qz.copy()
