
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

    def save(self):
        with open(self.file_angle_calibs, 'w') as calib_file:
            json.dump(self.angle_to_setpoints, calib_file, ensure_ascii=False, indent=4)

    def _to_serial(self, mirror, angles):
        angles_ser = [0,0]
        for i in range(2):
            angles_ser[i] = self.angle_to_setpoints['scales'][mirror][i] * angles[i] + self.angle_to_setpoints['zeros'][mirror][i]
        return angles_ser
    def _to_serial_delta(self, mirror, angles):
        angles_ser = [0,0]
        for i in range(2):
            angles_ser[i] = self.angle_to_setpoints['scales'][mirror][i] * angles[i] 
        return angles_ser
        
    def _from_serial(self, mirror, angles):
        angles_real = [0,0]
        for i in range(2):
            angles_real[i] = (angles[i] - self.angle_to_setpoints['zeros'][mirror][i]) / self.angle_to_setpoints['scales'][mirror][i]
        return angles_real



    def read_pos(self, mirror):
        return self._from_serial(self.serial.read_pos(mirror))

    def move(self, mirror, angles):
        ser_angles = self._to_serial(mirror, angles)
        print(f"{mirror}  {angles} {ser_angles}")
        self.serial.serial_move(mirror, ser_angles)

    def delta_move(self, mirror, delta):
        ser_delta = self._to_serial_delta(mirror, delta)
        self.serial.serial_delta_move(mirror, ser_delta)

