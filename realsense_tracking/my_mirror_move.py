
import json
import os.path
from my_utils import *

class MyMirrorMove:

    def __init__(self, serial ):
        self.serial = serial
        self.no_mirrors = 8
        self.angle_to_setpoints = {}
        self.file_angle_calibs = 'angle_calibs.json'
        if os.path.exists(self.file_angle_calibs) :
            with open(self.file_angle_calibs, 'r') as calib_file:
                self.angle_to_setpoints = json.load(calib_file)
        else :
            self.angle_to_setpoints['scales'] = []
            self.angle_to_setpoints['scales'] = [[1,1] for i in range(self.no_mirrors)] 
            self.angle_to_setpoints['zeros'] = []
            self.angle_to_setpoints['zeros'] = [[0,0] for i in range(self.no_mirrors)] 
        
        for m in range(self.no_mirrors):
            self.move_q(m,(0,0))
        self.move_e()

    # INTERNAL CALCULATIONS
    #   raw = scale * sp + zero
    #   sp  = (raw - zero) / scale

    def _sp_to_raw(self, mirror, angles_sp):
        angles_raw = [0,0]
        for i in range(2):
            angles_raw[i] = self.angle_to_setpoints['scales'][mirror][i]  * angles_sp[i] + self.angle_to_setpoints['zeros'][mirror][i]
        return angles_raw

    def _sp_to_raw_delta(self, mirror, angles_sp_d):
        angles_raw = [0,0]
        for i in range(2):
            angles_raw[i] = self.angle_to_setpoints['scales'][mirror][i] * angles_sp_d[i] 
        return angles_raw
        
    def _raw_to_setpoint(self, mirror, angles_raw):
        angles_sp = [0,0]
        for i in range(2):
            angles_sp[i] = (angles_raw[i] - self.angle_to_setpoints['zeros'][mirror][i]) / self.angle_to_setpoints['scales'][mirror][i]
        return angles_sp

    # UTILS

    def save(self):
        with open(self.file_angle_calibs, 'w') as calib_file:
            json.dump(self.angle_to_setpoints, calib_file, ensure_ascii=False, indent=4)
            print("mirror move parameters saved")

    # MOVERS

    def read_angles(self, mirror):
        raw_angles = self.serial.read_pos(mirror)
        return self._raw_to_setpoint(mirror, raw_angles)

    def move(self, mirror, angles_sp):
        raw_angles = self._sp_to_raw(mirror, angles_sp)
        # print(f" MOVE ANGLE M:{mirror} : SP: {angles_sp} RAW:{raw_angles}")
        self.serial.serial_move(mirror, raw_angles)
    def move_q(self, mirror, angles_sp):
        raw_angles = self._sp_to_raw(mirror, angles_sp)
        # print(f" MOVE ANGLE M:{mirror} : SP: {angles_sp} RAW:{raw_angles}")
        self.serial.serial_move_q(mirror, raw_angles)
    def move_e(self):
        self.serial.serial_move_e()
    

    def delta_move(self, mirror, delta_sp):
        raw_delta = self._sp_to_raw_delta(mirror, delta_sp)
        self.serial.serial_delta_move(mirror, raw_delta)


    # CALIBRATORS

    def zero(self, mirror):
        raw_angles = self.serial.read_pos(mirror)
        for a in range(2):
            self.angle_to_setpoints['zeros'][mirror][a] = raw_angles[a]

    def scale(self, mirror, degrees):
        raw_angles = self.serial.read_pos(mirror)
        for a in range(2):
            self.angle_to_setpoints['scales'][mirror][a] = (raw_angles[a] - self.angle_to_setpoints['zeros'][mirror][a]) / degrees[a]
            
               