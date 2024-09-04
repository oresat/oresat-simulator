#!/usr/bin/env python
import struct
import socket
from dataclasses import dataclass
import serial
import pprint

array = []
new_array = []

#Server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    port = 40000
    sock.bind(("127.0.0.1", port))
    sock.listen()

    cSock, cAddr = sock.accept()

    data = cSock.recv(120) 
    print("\nHere is the unpacked version that we'll send as bytes.\n")
    for x, y, z in struct.iter_unpack('3f', data):
        new_array.append([x,y,z])

    pprint.pp(new_array)
    
    with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
        envoy = ser.write(data)#Can I send an array or does it need to be bytes

