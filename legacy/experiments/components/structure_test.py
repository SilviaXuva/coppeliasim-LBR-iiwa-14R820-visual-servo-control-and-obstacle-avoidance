from sim import CoppeliaSim, PyPlot
from utils import Experiment, Timer

class StructureTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "0.Base.ttt",
            "duration": 10.0,
        }

        super().__init__(
            test_id=1,
            name="structure_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            if self.config['scene'] is None:
                psim = PyPlot()
                psim.start()

                try:
                    while psim.get_sim_time() < self.config['duration']:
                        psim.step()
                finally:
                    psim.stop()

            else:
                csim = CoppeliaSim(scene=self.config["scene"])
                csim.start()

                try:
                    while csim.sim.getSimulationTime() < self.config["duration"]:
                        csim.step()
                finally:
                    csim.stop()

        self.save_results({
            "duration": float(t.duration),
        })
        self.teardown
