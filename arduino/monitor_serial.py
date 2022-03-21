import serial
from time import sleep
import sys

import msvcrt

# https://gist.github.com/matdombrock/fb4833cb3b288a3530eb9a03e3550ecf

COM = 'COM8'# /dev/ttyACM0 (Linux)
BAUD = 115200

ser = serial.Serial(COM, BAUD, timeout = .1)

print('Waiting for device');
print(ser.name)


send_str = ""
while True:
    val = ser.readline().decode()
    print(val, end="\r", flush=True)
    # https://python.tutorialink.com/non-blocking-console-input/
    if msvcrt.kbhit():
        typed_char = msvcrt.getch()
        if typed_char == b'\r':
            print("  . SENDING " +send_str)
            send_str += "\n"
            ser.write((send_str.encode()))
            send_str = ""
        else :
            send_str += typed_char.decode()
