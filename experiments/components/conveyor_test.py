from sim import CoppeliaSim, Conveyor
from utils import Experiment, Timer

class ConveyorTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "4.Vision-based.ttt",
            "duration": 10.0,
            "conveyor_vel": 1.0,  # m/s
        }

        super().__init__(
            test_id=4,
            name="conveyor_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            csim = CoppeliaSim(
                stepping=False,
                scene=self.config["scene"],
            )

            conveyor = Conveyor(csim.sim, self.config["conveyor_vel"])
            csim.add_object(conveyor)

            csim.start()

            try:
                while csim.sim.getSimulationTime() < self.config["duration"]:
                    csim.step()
            finally:
                csim.stop()

        self.save_results({
            "duration": float(t.duration),
        })
