from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from spatialmath import SE3

from control.trajectory.profiles import get_profile


@dataclass(slots=True)
class CartesianTrajectorySample:
    """
    Sample of a Cartesian trajectory.

    Attributes
    ----------
    t : float
        Global time [s].
    T : SE3
        End-effector pose at time `t`.
    x : np.ndarray
        Cartesian pose vector [x, y, z, rx, ry, rz].
    dx : np.ndarray
        Cartesian velocity vector.
    ddx : np.ndarray
        Cartesian acceleration vector.
    s : float
        Normalized path position in [0, 1].
    ds : float
        Time derivative of normalized path position [1/s].
    dds : float
        Second time derivative of normalized path position [1/s²].
    done : bool
        Whether the trajectory has reached its final time.
    """

    t: float
    T: SE3
    x: np.ndarray
    dx: np.ndarray
    ddx: np.ndarray
    s: float
    ds: float
    dds: float
    done: bool


class CartesianTrajectory:
    """
    Cartesian trajectory using scalar time scaling between two SE3 poses.

    Translation is interpolated linearly.
    Orientation is interpolated using roll-pitch-yaw interpolation in radians.

    Parameters
    ----------
    T_start : SE3
        Initial end-effector pose.
    T_goal : SE3
        Final end-effector pose.
    duration : float
        Total trajectory duration [s].
    profile : str, optional
        Time-scaling profile name. Supported values are "cubic" and "quintic".
        Default is "quintic".
    start_time : float, optional
        Global start time [s]. Default is 0.0.
    """

    def __init__(
        self,
        T_start: SE3,
        T_goal: SE3,
        duration: float,
        profile: str = "quintic",
        start_time: float = 0.0,
    ) -> None:
        if duration <= 0.0:
            raise ValueError(f"duration must be > 0. Got {duration}.")

        self.T_start = T_start
        self.T_goal = T_goal
        self.duration = float(duration)
        self.start_time = float(start_time)
        self.profile = get_profile(profile)

        self.p_start = np.asarray(T_start.t, dtype=float).reshape(3)
        self.p_goal = np.asarray(T_goal.t, dtype=float).reshape(3)
        self.dp = self.p_goal - self.p_start

        self.rpy_start = np.asarray(T_start.rpy(order="zyx"), dtype=float).reshape(3)
        self.rpy_goal = np.asarray(T_goal.rpy(order="zyx"), dtype=float).reshape(3)
        self.drpy = self._wrap_angle_diff(self.rpy_goal - self.rpy_start)

    @property
    def end_time(self) -> float:
        """
        Final global time of the trajectory [s].
        """
        return self.start_time + self.duration

    def reset(self, start_time: float = 0.0) -> None:
        """
        Reset the trajectory start time.

        Parameters
        ----------
        start_time : float, optional
            New global start time [s]. Default is 0.0.
        """
        self.start_time = float(start_time)

    def sample(self, t: float) -> CartesianTrajectorySample:
        """
        Sample the trajectory at global time `t`.

        Parameters
        ----------
        t : float
            Global time [s].

        Returns
        -------
        CartesianTrajectorySample
            Cartesian trajectory sample at time `t`.
        """
        t = float(t)
        tau = t - self.start_time

        if tau <= 0.0:
            x = self._pose_to_cart(self.T_start)
            return CartesianTrajectorySample(
                t=t,
                T=self.T_start,
                x=x,
                dx=np.zeros(6, dtype=float),
                ddx=np.zeros(6, dtype=float),
                s=0.0,
                ds=0.0,
                dds=0.0,
                done=False,
            )

        if tau >= self.duration:
            x = self._pose_to_cart(self.T_goal)
            return CartesianTrajectorySample(
                t=t,
                T=self.T_goal,
                x=x,
                dx=np.zeros(6, dtype=float),
                ddx=np.zeros(6, dtype=float),
                s=1.0,
                ds=0.0,
                dds=0.0,
                done=True,
            )

        s, ds, dds = self.profile.evaluate(tau=tau, duration=self.duration)

        p = self.p_start + s * self.dp
        rpy = self.rpy_start + s * self.drpy

        dp = ds * self.dp
        ddp = dds * self.dp

        drpy = ds * self.drpy
        ddrpy = dds * self.drpy

        T = SE3.Trans(p) * SE3.RPY(rpy, order="zyx")
        x = np.concatenate((p, rpy))
        dx = np.concatenate((dp, drpy))
        ddx = np.concatenate((ddp, ddrpy))

        return CartesianTrajectorySample(
            t=t,
            T=T,
            x=x,
            dx=dx,
            ddx=ddx,
            s=s,
            ds=ds,
            dds=dds,
            done=False,
        )

    def __call__(self, t: float) -> CartesianTrajectorySample:
        """
        Alias for `sample`.

        Parameters
        ----------
        t : float
            Global time [s].

        Returns
        -------
        CartesianTrajectorySample
            Cartesian trajectory sample at time `t`.
        """
        return self.sample(t)

    def is_finished(self, t: float) -> bool:
        """
        Check whether the trajectory is finished at time `t`.

        Parameters
        ----------
        t : float
            Global time [s].

        Returns
        -------
        bool
            True if the trajectory has ended, otherwise False.
        """
        return float(t) >= self.end_time

    def sample_times(
        self,
        times: np.ndarray | list[float],
    ) -> tuple[list[SE3], np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample the trajectory over an array of global times.

        Parameters
        ----------
        times : np.ndarray | list[float]
            Sampling times [s].

        Returns
        -------
        tuple[list[SE3], np.ndarray, np.ndarray, np.ndarray]
            T_list, x, dx, ddx
        """
        times = np.asarray(times, dtype=float).reshape(-1)

        T_list: list[SE3] = []
        x_list = []
        dx_list = []
        ddx_list = []

        for t in times:
            sample = self.sample(float(t))
            T_list.append(sample.T)
            x_list.append(sample.x)
            dx_list.append(sample.dx)
            ddx_list.append(sample.ddx)

        return (
            T_list,
            np.vstack(x_list),
            np.vstack(dx_list),
            np.vstack(ddx_list),
        )

    def discretize(
        self,
        dt: float,
        include_endpoint: bool = True,
    ) -> tuple[np.ndarray, list[SE3], np.ndarray, np.ndarray, np.ndarray]:
        """
        Discretize the trajectory using a fixed time step.

        Parameters
        ----------
        dt : float
            Time step [s].
        include_endpoint : bool, optional
            Whether to include the final sample at `end_time`.
            Default is True.

        Returns
        -------
        tuple[np.ndarray, list[SE3], np.ndarray, np.ndarray, np.ndarray]
            times, T_list, x, dx, ddx
        """
        if dt <= 0.0:
            raise ValueError(f"dt must be > 0. Got {dt}.")

        times = np.arange(self.start_time, self.end_time, dt, dtype=float)

        if include_endpoint:
            if len(times) == 0 or not np.isclose(times[-1], self.end_time):
                times = np.append(times, self.end_time)

        T_list, x, dx, ddx = self.sample_times(times)
        return times, T_list, x, dx, ddx

    @staticmethod
    def _pose_to_cart(T: SE3) -> np.ndarray:
        """
        Convert SE3 pose to Cartesian vector [x, y, z, rx, ry, rz].

        Parameters
        ----------
        T : SE3
            Pose.

        Returns
        -------
        np.ndarray
            Cartesian pose vector.
        """
        p = np.asarray(T.t, dtype=float).reshape(3)
        rpy = np.asarray(T.rpy(order="zyx"), dtype=float).reshape(3)
        return np.concatenate((p, rpy))

    @staticmethod
    def _wrap_angle_diff(angle_diff: np.ndarray) -> np.ndarray:
        """
        Wrap angular difference to [-pi, pi].

        Parameters
        ----------
        angle_diff : np.ndarray
            Angular difference array.

        Returns
        -------
        np.ndarray
            Wrapped angular difference.
        """
        return (angle_diff + np.pi) % (2.0 * np.pi) - np.pi
