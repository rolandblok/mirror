from numpy import true_divide
import serial
import time


class MyMirrorSerial:

    def __init__(self, port):
        self.serial_connected = False
        if port != "":
            from serial.tools import list_ports
            com_ports = list_ports.comports()
            print("com ports")
            for com_port in com_ports:
                print("  " + com_port.description + " " + com_port.device)
            self.ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(1)
            print("serial connected : {}".format(self.ser.readline().decode()))
            self.serial_open = True

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
            self.ser.write(("raw\n".encode()))
            mir_pos = self.ser.readline().decode().split(',')
        return mir_pos

    def serial_move(self, point):
        if (self.serial_connected):
            print("{}".format(self.serial_write_and_read("a {}".format(point[X]))))
            print("{}".format(self.serial_write_and_read("b {}".format(point[Y]))))
            time.sleep(0.2)
        else:
            print("serial not connected")

    def close(self):
        self.ser.close()