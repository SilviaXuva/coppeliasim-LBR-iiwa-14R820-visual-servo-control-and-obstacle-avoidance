from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .time_parameterization import validate_duration


@dataclass(frozen=True)
class QuinticBoundaryConditions:
    q0: float
    qf: float
    v0: float = 0.0
    vf: float = 0.0
    a0: float = 0.0
    af: float = 0.0


@dataclass(frozen=True)
class QuinticPolynomial:
    """
    Scalar quintic polynomial trajectory.

    q(t) = a0 + a1 t + a2 t^2 + a3 t^3 + a4 t^4 + a5 t^5
    """
    coefficients: np.ndarray
    duration: float

    @staticmethod
    def from_boundary_conditions(boundary: QuinticBoundaryConditions, duration: float) -> "QuinticPolynomial":
        validate_duration(duration)

        T = duration
        q0, qf = boundary.q0, boundary.qf
        v0, vf = boundary.v0, boundary.vf
        a0, af = boundary.a0, boundary.af

        c0 = q0
        c1 = v0
        c2 = a0 / 2.0

        A = np.array(
            [
                [T**3, T**4, T**5],
                [3*T**2, 4*T**3, 5*T**4],
                [6*T, 12*T**2, 20*T**3],
            ],
            dtype=float,
        )

        b = np.array(
            [
                qf - (c0 + c1*T + c2*T**2),
                vf - (c1 + 2*c2*T),
                af - (2*c2),
            ],
            dtype=float,
        )

        c3, c4, c5 = np.linalg.solve(A, b)
        coeffs = np.array([c0, c1, c2, c3, c4, c5], dtype=float)
        return QuinticPolynomial(coefficients=coeffs, duration=duration)

    def evaluate(self, t: float) -> tuple[float, float, float]:
        if t < 0.0 or t > self.duration:
            raise ValueError("t must be inside [0, duration].")

        c0, c1, c2, c3, c4, c5 = self.coefficients

        q = c0 + c1*t + c2*t**2 + c3*t**3 + c4*t**4 + c5*t**5
        v = c1 + 2*c2*t + 3*c3*t**2 + 4*c4*t**3 + 5*c5*t**4
        a = 2*c2 + 6*c3*t + 12*c4*t**2 + 20*c5*t**3

        return float(q), float(v), float(a)
