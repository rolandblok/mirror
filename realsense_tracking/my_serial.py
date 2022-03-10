from numpy import true_divide
import serial
import time
from my_utils import *


class MyMirrorSerial:

    def __init__(self, port, debug_on = False):
        self.serial_connected = False
        self.debug_on = debug_on

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

    def serial_write_and_read(self, ser_com):
        if (self.serial_connected):
            self.ser.reset_input_buffer()
            self.ser.write("{}\n".format(ser_com).encode())
            self.ser.flush()
            return self.ser.readline().decode()
        else:
            return ""

    def read_pos(self):
        mir_pos = [0,0]
        if (self.serial_connected):
            self.ser.reset_input_buffer()
            self.ser.write(("logpos\n".encode()))
            mir_pos = self.ser.readline().decode().split(',')
            mir_pos = [int(mp) for mp in mir_pos]
        return mir_pos

    def serial_move(self, point):
        if (self.serial_connected):
            angles = self.serial_write_and_read("c {}, {}".format(point[X], point[Y]))
            if self.debug_on:
                print("{}".format(angles))
        else:
            print("serial not connected")

    def serial_delta_move(self, delta_x, delta_y):
        if (self.serial_connected):
            delta_x = round(delta_x)
            delta_y = round(delta_y)
            angles = self.serial_write_and_read("C {}, {}".format(delta_x, delta_y))
            if self.debug_on:
                print("{}".format(angles))
        else:
            print("serial not connected")


    def close(self):
        self.ser.close()