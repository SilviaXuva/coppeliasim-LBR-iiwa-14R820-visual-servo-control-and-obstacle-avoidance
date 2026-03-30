from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning import QuinticBoundaryConditions, QuinticPolynomial


def test_quintic_polynomial_matches_boundary_conditions() -> None:
    boundary = QuinticBoundaryConditions(q0=0.0, qf=1.0, v0=0.0, vf=0.0, a0=0.0, af=0.0)
    profile = QuinticPolynomial.from_boundary_conditions(boundary, duration=2.0)

    q0, v0, a0 = profile.evaluate(0.0)
    qf, vf, af = profile.evaluate(2.0)

    assert np.isclose(q0, 0.0)
    assert np.isclose(v0, 0.0)
    assert np.isclose(a0, 0.0)
    assert np.isclose(qf, 1.0)
    assert np.isclose(vf, 0.0)
    assert np.isclose(af, 0.0)
