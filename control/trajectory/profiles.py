from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CubicProfile:
    """
    Cubic time-scaling profile with zero initial and final velocity.

    The normalized path parameter is:

        s(u) = 3u² - 2u³

    where u = tau / duration, u in [0, 1].
    """

    def evaluate(self, tau: float, duration: float) -> tuple[float, float, float]:
        """
        Evaluate the cubic time-scaling profile.

        Parameters
        ----------
        tau : float
            Local trajectory time [s].
        duration : float
            Total trajectory duration [s].

        Returns
        -------
        tuple[float, float, float]
            s, ds, dds
        """
        if duration <= 0.0:
            raise ValueError(f"duration must be > 0. Got {duration}.")

        if tau <= 0.0:
            return 0.0, 0.0, 0.0

        if tau >= duration:
            return 1.0, 0.0, 0.0

        u = tau / duration

        s = 3.0 * u**2 - 2.0 * u**3
        ds_du = 6.0 * u - 6.0 * u**2
        dds_du2 = 6.0 - 12.0 * u

        ds = ds_du / duration
        dds = dds_du2 / (duration**2)

        return s, ds, dds


@dataclass(slots=True)
class QuinticProfile:
    """
    Quintic time-scaling profile with zero initial/final velocity
    and zero initial/final acceleration.

    The normalized path parameter is:

        s(u) = 10u³ - 15u⁴ + 6u⁵

    where u = tau / duration, u in [0, 1].
    """

    def evaluate(self, tau: float, duration: float) -> tuple[float, float, float]:
        """
        Evaluate the quintic time-scaling profile.

        Parameters
        ----------
        tau : float
            Local trajectory time [s].
        duration : float
            Total trajectory duration [s].

        Returns
        -------
        tuple[float, float, float]
            s, ds, dds
        """
        if duration <= 0.0:
            raise ValueError(f"duration must be > 0. Got {duration}.")

        if tau <= 0.0:
            return 0.0, 0.0, 0.0

        if tau >= duration:
            return 1.0, 0.0, 0.0

        u = tau / duration

        s = 10.0 * u**3 - 15.0 * u**4 + 6.0 * u**5
        ds_du = 30.0 * u**2 - 60.0 * u**3 + 30.0 * u**4
        dds_du2 = 60.0 * u - 180.0 * u**2 + 120.0 * u**3

        ds = ds_du / duration
        dds = dds_du2 / (duration**2)

        return s, ds, dds


def get_profile(name: str):
    """
    Build a supported time-scaling profile by name.

    Parameters
    ----------
    name : str
        Profile name. Supported:
        - "cubic"
        - "quintic"

    Returns
    -------
    CubicProfile | QuinticProfile
        Instantiated profile object.
    """
    normalized_name = name.strip().lower()

    if normalized_name == "cubic":
        return CubicProfile()

    if normalized_name == "quintic":
        return QuinticProfile()

    raise ValueError(
        f"Unsupported profile '{name}'. Supported profiles: ['cubic', 'quintic']."
    )