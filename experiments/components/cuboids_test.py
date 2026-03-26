from sim import CoppeliaSim, Conveyor, Cuboids
from utils import Experiment, Timer

class CuboidsTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "4.Vision-based.ttt",
            "duration": 30.0,
            "conveyor_vel": 1.0,  # m/s
            "cuboids_max_creation": 5,
        }

        super().__init__(
            test_id=5,
            name="cuboids_test",
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

            cuboids = Cuboids(csim.sim, self.config["cuboids_max_creation"])
            csim.add_object(cuboids)

            csim.start()

            try:
                while csim.sim.getSimulationTime() < self.config["duration"]:
                    max_created = (
                        cuboids.max_creation is not None
                        and len(cuboids.created) >= cuboids.max_creation
                    )
                    no_pending = not cuboids.check_pending()

                    if max_created and no_pending:
                        break

                    csim.step()
            finally:
                csim.stop()

        self.save_results({
            "duration": float(t.duration),
            "created_cuboids": len(cuboids.created),
        })
