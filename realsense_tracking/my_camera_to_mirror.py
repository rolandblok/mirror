import numpy as np
import math

import json
from json import JSONEncoder
import os.path
from my_utils import *


# CONSTANTS
X = 0   # array indices for cartesian dimensions
Y = 1
Z = 2
A = 0   # array indices for mirror angles
B = 1

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)

class MyCameraToMirror:
        def __init__(self):
            self.calib_params = [0,0,0,0,0,0,0,0]

            #         2 
            #     3        1
            # 7                 6          
            #     4        0
            #         5 
            self.file_angle_calibs = 'cam2mir_calibs.json'
            if os.path.exists(self.file_angle_calibs) :
                with open(self.file_angle_calibs, 'r') as calib_file:
                    self.calib_params = json.load(calib_file)
            else :
                self.calib_params[0] = np.array([0.181865,  0.15, 0])
                self.calib_params[1] = np.array([0.181865, -0.15, 0])

                self.calib_params[2] = np.array([0, -0.21, 0])

                self.calib_params[3] = np.array([-0.181865, -0.15, 0])
                self.calib_params[4] = np.array([-0.181865, +0.15, 0])

                self.calib_params[5] = np.array([0,  0.21, 0])

                self.calib_params[6] = np.array([ 0.363731, 0, 0])
                self.calib_params[7] = np.array([-0.363731, 0, 0])


        def get_angle(self, mirror, pos_cam_3d):
            cp = self.calib_params[mirror]
            f_m = -np.array(pos_cam_3d) + cp 
            angle = [0,0]
            angle[A] = -math.atan(f_m[X] / f_m[Z]) * 180 / math.pi
            angle[B] = -math.atan(f_m[Y] / f_m[Z]) * 180 / math.pi
            # print(f"get angle {pos_cam_3d} {f_m} {angle}")
            return angle

        def zero_angle(self, mirror, angle, pos_cam_3d):
            self.calib_params[mirror][X] = pos_cam_3d[Z]*math.tan(angle[A]*math.pi/180) + pos_cam_3d[X]
            self.calib_params[mirror][Y] = pos_cam_3d[Z]*math.tan(angle[B]*math.pi/180) + pos_cam_3d[Y]
            print(f"zero_angle M {mirror} : {self.calib_params[mirror]} ")

        def save(self):
            with open(self.file_angle_calibs, 'w') as calib_file:
                json.dump(self.calib_params, calib_file, ensure_ascii=False, indent=4, cls=NumpyArrayEncoder)
                print("camera to mirrors saved")