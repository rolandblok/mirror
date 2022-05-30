from numpy import true_divide
import serial
import time
from my_utils import *



class MyMirrorSerial:

    def __init__(self, port, debug_on = False):
        self.serial_connected = False
        self.debug_on = debug_on
        self.mirror_que = [[0 for x in range(NO_ANGLES_PER_MIRROR)] for i in range(NO_MIRRORS)]

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
        else :
            print('Serial emulator')

    # ==================
    # internal 
    def _serial_write(self, ser_com):
        if (self.debug_on):
            print(" SERCOM : " + ser_com)
        if self.serial_connected:
            self.ser.reset_input_buffer()
            self.ser.write("{}\n".format(ser_com).encode())
            self.ser.flush()
            return True
        else :
            return False

    def _serial_write_and_read(self, ser_com):
        if self._serial_write(ser_com):
            # time.sleep(0.05)
            ret = self.ser.readline().decode()
            if self.debug_on:
                print(" SERRET : " + ret)
            return ret
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

    def serial_move(self, mirror, angle):
        # self._serial_write("c,{},{:.2f},{:.2f}".format(mirror, angle[A], angle[B]))
        self._serial_write_and_read("c,{},{:.2f},{:.2f}".format(mirror, angle[A], angle[B]))
        # self._serial_write("c,{},{},{}".format(mirror, angle[A], angle[B]))

    def serial_move_q(self, mirror, angles):
        self.mirror_que[mirror] = angles

    # d,-21.39,-17.54,-22.48,-23.17,-20.64,-35.33,-28.81,-28.89,-32.75,-23.41,-20.78,-31.97,-55.71,-28.06,-57.81,-28.08

    def serial_move_e(self):
        command = "d"
        for m in range(0,4):
            ma = self.mirror_que[m]
            for a in ma:
                command += ",{:.2f}".format(a)
        self._serial_write_and_read(command)
        command = "e"
        for m in range(4,8):
            ma = self.mirror_que[m]
            for a in ma:
                command += ",{:.2f}".format(a)
        self._serial_write_and_read(command)

    def serial_delta_move(self, mirror, delta):
        print("C,{},{:.2f},{:.2f}".format(mirror, delta[A], delta[B]))
        self._serial_write_and_read("C,{},{:.2f},{:.2f}".format(mirror, delta[A], delta[B]))

    def serial_mirror_smooth(self, enable) :
        if enable:
            self._serial_write("son")
        else :
            self._serial_write("soff")
    
    def serial_mirror_select(self, mirror) :
        self._serial_write(f"m,{mirror}")

    def close(self):
        if self.serial_connected:
            self.ser.close()