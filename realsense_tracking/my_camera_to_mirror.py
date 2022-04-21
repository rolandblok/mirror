import numpy as np
import math

# CONSTANTS
X = 0   # array indices for cartesian dimensions
Y = 1
Z = 2
A = 0   # array indices for mirror angles
B = 1

class MyCameraToMirror:
        def __init__(self):
            self.calib_params = [0,0,0,0,0,0,0,0]


            #         2 
            #     3        1
            # 7                 6          
            #     4        0
            #         5 

            self.calib_params[0] = np.array([0.181865, -0.15, 0])
            self.calib_params[1] = np.array([0.181865,  0.15, 0])

            self.calib_params[2] = np.array([0, 0.21, 0])

            self.calib_params[3] = np.array([-0.181865,  0.15, 0])
            self.calib_params[4] = np.array([-0.181865, -0.15, 0])

            self.calib_params[5] = np.array([0, -0.21, 0])

            self.calib_params[6] = np.array([ 0.363731, 0, 0])
            self.calib_params[7] = np.array([-0.363731, 0, 0])


        def get_angle(self, mirror, pos_cam_3d):
            cp = self.calib_params[mirror]
            f_m = np.array(pos_cam_3d) + cp
            angle = [0,0]
            angle[A] = math.atan(f_m[Z] / f_m[X])
            angle[B] = math.atan(f_m[Z] / f_m[Y])
            return angle


