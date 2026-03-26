from __future__ import annotations

import numpy as np

from control.trajectory.base import JointTrajectorySample, TimeScalingProfile
from control.trajectory.profiles import QuinticProfile, get_profile


class JointTrajectory:
    """
    Joint-space trajectory using scalar time scaling.

    The trajectory is defined between `q_start` and `q_goal` and evaluated as:

        q(t)   = q_start + s(t)   * (q_goal - q_start)
        dq(t)  =           ds(t)  * (q_goal - q_start)
        ddq(t) =           dds(t) * (q_goal - q_start)

    Parameters
    ----------
    q_start : np.ndarray | list[float]
        Initial joint configuration.
    q_goal : np.ndarray | list[float]
        Final joint configuration.
    duration : float
        Total trajectory duration [s].
    profile : str | TimeScalingProfile, optional
        Time-scaling profile. If a string is provided, supported values are
        "cubic" and "quintic". Default is "quintic".
    start_time : float, optional
        Global start time [s]. Default is 0.0.
    """

    def __init__(
        self,
        q_start: np.ndarray | list[float],
        q_goal: np.ndarray | list[float],
        duration: float,
        profile: str | TimeScalingProfile = "quintic",
        start_time: float = 0.0,
    ) -> None:
        self.q_start = np.asarray(q_start, dtype=float).reshape(-1)
        self.q_goal = np.asarray(q_goal, dtype=float).reshape(-1)

        if self.q_start.shape != self.q_goal.shape:
            raise ValueError(
                "q_start and q_goal must have the same shape. "
                f"Got {self.q_start.shape} and {self.q_goal.shape}."
            )

        if duration <= 0.0:
            raise ValueError(f"duration must be > 0. Got {duration}.")

        self.duration = float(duration)
        self.start_time = float(start_time)
        self.delta_q = self.q_goal - self.q_start
        self.n_joints = self.q_start.size

        if isinstance(profile, str):
            self.profile = get_profile(profile)
        else:
            self.profile = profile

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

    def sample(self, t: float) -> JointTrajectorySample:
        """
        Sample the trajectory at global time `t`.

        Parameters
        ----------
        t : float
            Global time [s].

        Returns
        -------
        JointTrajectorySample
            Joint trajectory sample at time `t`.
        """
        t = float(t)
        tau = t - self.start_time

        if tau <= 0.0:
            return JointTrajectorySample(
                t=t,
                q=self.q_start.copy(),
                dq=np.zeros_like(self.q_start),
                ddq=np.zeros_like(self.q_start),
                s=0.0,
                ds=0.0,
                dds=0.0,
                done=False,
            )

        if tau >= self.duration:
            return JointTrajectorySample(
                t=t,
                q=self.q_goal.copy(),
                dq=np.zeros_like(self.q_goal),
                ddq=np.zeros_like(self.q_goal),
                s=1.0,
                ds=0.0,
                dds=0.0,
                done=True,
            )

        s, ds, dds = self.profile.evaluate(tau=tau, duration=self.duration)

        q = self.q_start + s * self.delta_q
        dq = ds * self.delta_q
        ddq = dds * self.delta_q

        return JointTrajectorySample(
            t=t,
            q=q,
            dq=dq,
            ddq=ddq,
            s=s,
            ds=ds,
            dds=dds,
            done=False,
        )

    def __call__(self, t: float) -> JointTrajectorySample:
        """
        Alias for `sample`.

        Parameters
        ----------
        t : float
            Global time [s].

        Returns
        -------
        JointTrajectorySample
            Joint trajectory sample at time `t`.
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
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample the trajectory over an array of global times.

        Parameters
        ----------
        times : np.ndarray | list[float]
            Sampling times [s].

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray]
            q, dq, ddq arrays with shape (N, n_joints).
        """
        times = np.asarray(times, dtype=float).reshape(-1)

        q_list = []
        dq_list = []
        ddq_list = []

        for t in times:
            sample = self.sample(float(t))
            q_list.append(sample.q)
            dq_list.append(sample.dq)
            ddq_list.append(sample.ddq)

        return np.vstack(q_list), np.vstack(dq_list), np.vstack(ddq_list)

    def discretize(
        self,
        dt: float,
        include_endpoint: bool = True,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            times, q, dq, ddq
        """
        if dt <= 0.0:
            raise ValueError(f"dt must be > 0. Got {dt}.")

        times = np.arange(self.start_time, self.end_time, dt, dtype=float)

        if include_endpoint:
            if len(times) == 0 or not np.isclose(times[-1], self.end_time):
                times = np.append(times, self.end_time)

        q, dq, ddq = self.sample_times(times)
        return times, q, dq, ddq

    @classmethod
    def from_duration_and_goal(
        cls,
        q_start: np.ndarray | list[float],
        q_goal: np.ndarray | list[float],
        duration: float,
    ) -> "JointTrajectory":
        """
        Convenience constructor using the default quintic profile.

        Parameters
        ----------
        q_start : np.ndarray | list[float]
            Initial joint configuration.
        q_goal : np.ndarray | list[float]
            Final joint configuration.
        duration : float
            Total trajectory duration [s].

        Returns
        -------
        JointTrajectory
            Configured joint trajectory.
        """
        return cls(
            q_start=q_start,
            q_goal=q_goal,
            duration=duration,
            profile=QuinticProfile(),
        )