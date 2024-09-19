import struct
import serial
import pprint

with serial.Serial(port = "/dev/ttyUSB1", baudrate = 115200) as ser:
    while True:
        data = ser.read(1200)
        if len(data) > 0:
            break 


    new_array = [[x,y,z] for x, y, z in struct.iter_unpack('3f', data)]
    pprint.pp(new_array)
