from numpy import true_divide
import serial
import time
from my_utils import *


class MyMirrorSerial:

    def __init__(self, port, debug_on = False):
        self.serial_connected = True
        self.debug_on = debug_on
        self.swap_XY = True

        if port != "":
            from serial.tools import list_ports
            com_ports = list_ports.comports()
            print("com ports")
            for com_port in com_ports:
                print("  " + com_port.description + " " + com_port.device)
            self.ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(1)
            print("serial connected : {}".format(self.ser.readline().decode()))
            self.serial_connected = True

    # ==================
    # internal 
    def _serial_write(self, ser_com):
        if self.serial_connected:
            self.ser.reset_input_buffer()
            self.ser.write("{}\n".format(ser_com).encode())
            self.ser.flush()
            return True
        else :
            return False

    def _serial_write_and_read(self, ser_com):
        if self._serial_write(ser_com):
            return self.ser.readline().decode()
        else:
            return ""

    # ==================
    # externals
    def read_pos(self, mirror):
        mir_pos = [0,0]
        ser_com = "km,{}\n".format(mirror)
        mir_pos = self._serial_write_and_read(ser_com).split(',')
        mir_pos = [int(mp) for mp in mir_pos]
        return mir_pos

    def serial_move(self, mirror, point):
        if (self.swap_XY):
            point[Y], point[X] = point[X], point[Y]
        self._serial_write_and_read("c,{},{},{}".format(mirror,point[X], point[Y]))

    def serial_delta_move(self, mirror, delta_x, delta_y):
        delta_x = round(delta_x)
        delta_y = round(delta_y)
        if (self.swap_XY):
            delta_y, delta_x = delta_x, delta_y
        self._serial_write_and_read("C,{},{},{}".format(mirror,delta_x, delta_y))

    def close(self):
        self.ser.close()