from Helpers.paths import Paths
import os
Paths.execution = fr'{Paths.output}\{os.path.splitext(os.path.basename(__file__))[0]}\{os.path.splitext(os.path.basename(Paths.execution))[0]}'
os.makedirs(Paths.execution, exist_ok=True)
from Helpers.log import Log

from Helpers.Analysis.plotVision import plotOutputs
from Helpers.input import Aruco
from Models import DH_LBR_iiwa
from Simulators import CoppeliaSim
from Simulators.CoppeliaSim import Drawing, RobotiqGripper, Camera, Conveyor, Cuboids
from VisionProcessing.aruco import ArucoVision

robot = DH_LBR_iiwa()
coppelia = CoppeliaSim(scene='2.test_vision.ttt')
coppelia.Drawing = Drawing()
coppelia.Gripper = RobotiqGripper()
coppelia.Camera = Camera()
coppelia.ArucoVision = ArucoVision(coppelia.Camera)
coppelia.Conveyor = Conveyor()
coppelia.Cuboids = Cuboids()

robot = coppelia.Start(robot)

useExtrinsicGuessOptions = [True, False]
solvePnPMethodOptions = range(9)
for useExtrinsicGuess in useExtrinsicGuessOptions:
    Aruco.estimateParam.useExtrinsicGuess = useExtrinsicGuess
    for solvePnPMethod in solvePnPMethodOptions:
        Aruco.estimateParam.solvePnPMethod = solvePnPMethod
        Log('ArUco parameters: ')
        Log('Use Extrinsic Guess: ', useExtrinsicGuess)
        Log('Solve PNP Method: ', solvePnPMethod)
        for i in range(10):
            for marker in coppelia.ArucoVision.allDetected:
                coppelia.ArucoVision.PrintEstimatedPose(marker)
            coppelia.Step()

coppelia.Stop()

plotOutputs(Paths.execution)

import time
import glob
import shutil
import os
time.sleep(5)
try:
    recordingFile = glob.glob(r'*.avi')[0]
    shutil.move(recordingFile, fr'{Paths.execution}\recording.avi')
except Exception as e:
    print(e)