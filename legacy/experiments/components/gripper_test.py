from sim import CoppeliaSim, Robotiq2F85
from utils import Experiment, Timer

class GripperTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "4.Vision-based.ttt",
            "duration": 20.0,
        }

        super().__init__(
            test_id=7,
            name="gripper_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            csim = CoppeliaSim(
                stepping=True,
                scene=self.config["scene"],
            )

            gripper = Robotiq2F85(client=csim.client, sim=csim.sim)
            csim.add_object(gripper)

            csim.start()

            phase = None

            try:
                while csim.sim.getSimulationTime() < self.config["duration"]:
                    sim_time = csim.sim.getSimulationTime()

                    if sim_time < 5.0:
                        new_phase = "idle_1"
                    elif sim_time < 10.0:
                        new_phase = "close"
                    elif sim_time < 15.0:
                        new_phase = "idle_2"
                    else:
                        new_phase = "open"

                    if new_phase != phase:
                        phase = new_phase

                        if phase in {"idle_1", "idle_2"}:
                            gripper.stop_motion()
                        elif phase == "close":
                            gripper.close()
                        elif phase == "open":
                            gripper.open()

                    csim.step()
            finally:
                csim.stop()

        self.save_results({
            "duration": float(t.duration),
            "is_open_final": gripper.is_open(),
        })
