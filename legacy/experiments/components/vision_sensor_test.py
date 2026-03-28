from sim import CoppeliaSim, VisionDepthSensor, VisionSensor
from utils import Experiment, Timer

class VisionSensorTest(Experiment):
    def __init__(self, config: dict | None = None) -> None:
        default_config = {
            "scene": "2.ArUco_rgb.ttt",
            "vision_sensor_type": "RGB",
            "sensor_path": "./rgb",
            "rgb_sensor_path": "./kinect/joint/rgb",
            "depth_sensor_path": "./kinect/joint/depth",
            "duration": 10.0,
        }

        super().__init__(
            test_id=2,
            name="vision_sensor_test",
            config=config or default_config,
        )

    def _run(self) -> None:
        with Timer("simulation", self.logger) as t:
            csim = CoppeliaSim(
                stepping=False,
                scene=self.config["scene"],
            )

            sensor_type = self.config["vision_sensor_type"]

            if sensor_type == "RGB":
                vs = VisionSensor(
                    csim.sim,
                    sensor_path=self.config["sensor_path"],
                )
            elif sensor_type == "RGB-D":
                vs = VisionDepthSensor(
                    csim.sim,
                    rgb_sensor_path=self.config["rgb_sensor_path"],
                    depth_sensor_path=self.config["depth_sensor_path"],
                )
            else:
                raise ValueError(
                    f"Invalid vision_sensor_type '{sensor_type}'. "
                    "Expected 'RGB' or 'RGB-D'."
                )

            csim.add_object(vs)
            csim.start()

            try:
                while csim.sim.getSimulationTime() < self.config["duration"]:
                    csim.step()
            finally:
                csim.stop()

        self.save_results({
            "duration": float(t.duration),
        })
