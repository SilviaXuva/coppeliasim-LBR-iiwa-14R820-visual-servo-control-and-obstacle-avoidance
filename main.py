from experiments import (
    # ConveyorTest,
    # CuboidsTest,
    # GripperTest,
    RobotTest,
    StructureTest,
    # TrajDrawingTest,
    # VisionSensorTest
)
from utils import DEG_TO_RAD

if __name__ == "__main__":
    StructureTest(
        config={
            "scene": None,
            "duration": 10.0,
        }
    ).run()

    StructureTest(
        config={
            "scene": "0.Base.ttt",
            "duration": 10.0,
        }
    ).run()

    RobotTest(
        config={
            "scene": None,
            "duration": 10.0,
            "robot_target_vel": [0, 0, 0, 0, 0, 0, 90 * DEG_TO_RAD],
        }
    ).run()

    RobotTest(
        config={
            "scene": "1.LBR_iiwa.ttt",
            "duration": 10.0,
            "robot_target_vel": [0, 0, 0, 0, 0, 0, 90 * DEG_TO_RAD],
        }
    ).run()
    
    # VisionSensorTest(
    #     config={
    #         "scene": "2.ArUco_rgb.ttt",
    #         "vision_sensor_type": "RGB",
    #         "sensor_path": "./rgb",
    #         "duration": 30.0,
    #     }
    # ).run()

    # VisionSensorTest(
    #     config={
    #         "scene": "3.ArUco_kinect.ttt",
    #         "vision_sensor_type": "RGB-D",
    #         "depth_sensor_path": "./kinect/joint/depth",
    #         "rgb_sensor_path": "./kinect/joint/rgb",
    #         "duration": 30.0,
    #     }
    # ).run()

    # ConveyorTest(
    #     config={
    #         "scene": "4.Vision-based.ttt",
    #         "duration": 10.0,
    #         "conveyor_vel": 1.0,  # m/s
    #     }
    # ).run()

    # CuboidsTest(
    #     config={
    #         "scene": "4.Vision-based.ttt",
    #         "duration": 30.0,
    #         "conveyor_vel": 1.0,  # m/s
    #         "cuboids_max_creation": 5,
    #     }
    # ).run()

    # TrajDrawingTest(
    #     config={
    #         "scene": "4.Vision-based.ttt",
    #         "duration": 10.0,
    #         "robot_target_vel": [90 * DEG_TO_RAD, 0, 0, 0, 0, 0, 90 * DEG_TO_RAD],
    #     }
    # ).run()

    # GripperTest(
    #     config={
    #         "scene": "4.Vision-based.ttt",
    #         "duration": 20.0,
    #     }
    # ).run()
