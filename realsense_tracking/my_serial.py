from numpy import true_divide
import serial
import time
from my_utils import *


class MyMirrorSerial:

    def __init__(self, port, debug_on = False):
        self.serial_connected = True
        self.debug_on = debug_on
        self.swap_XY = False

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
        ser_ans = self._serial_write_and_read(ser_com)
        # print("{}".format(ser_ans))
        mir_pos = ser_ans.split(',')
        mir_pos = (float(mir_pos[1]), float(mir_pos[2]))
        return mir_pos

    def serial_move(self, mirror, point):
        if (self.swap_XY):
            point[Y], point[X] = point[X], point[Y]
        self._serial_write_and_read("c,{},{},{}".format(mirror,point[X], point[Y]))

    def serial_delta_move(self, mirror, delta_x, delta_y):
        delta_x = delta_x
        delta_y = delta_y
        if (self.swap_XY):
            delta_y, delta_x = delta_x, delta_y
        print("C,{},{:.2f},{:.2f}".format(mirror,delta_x, delta_y))
        self._serial_write_and_read("C,{},{:.2f},{:.2f}".format(mirror,delta_x, delta_y))

    def serial_mirror_smooth(self, enable) :
        if enable:
            self._serial_write("son")
        else :
            self._serial_write("soff")
    
    def serial_mirror_select(self, mirror) :
        self._serial_write(f"m,{mirror}")
    


    def close(self):
        self.ser.close()