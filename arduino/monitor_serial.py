import serial
from time import sleep
import sys
import msvcrt

# https://gist.github.com/matdombrock/fb4833cb3b288a3530eb9a03e3550ecf

from serial.tools import list_ports
av_com_ports = list_ports.comports()
print("com ports")
for av_com_port in av_com_ports:
    print("  " + av_com_port.description + " " + av_com_port.device)

 
print(f'Argumenent {sys.argv[0]}')
 
if len(sys.argv) > 1:
    COM = sys.argv[1]
else:
    COM = 'COM8'
print("connecting to {}".format(COM))



BAUD = 115200

ser = serial.Serial(COM, BAUD, timeout = .1)

print('Waiting for device');
print(ser.name)


send_str = ""
while True:
    val = ser.readline().decode(encoding='UTF-8',errors='replace')
    print(val, end="", flush=True)
    # https://python.tutorialink.com/non-blocking-console-input/
    if msvcrt.kbhit():
        typed_char = msvcrt.getch()
        if typed_char == b'\x1b':  # quit on escape
            quit()        
        elif typed_char == b'\r':
            print("  . SENDING " +send_str)
            send_str += "\n"
            ser.write((send_str.encode()))
            send_str = ""
        else :
            send_str += typed_char.decode()
