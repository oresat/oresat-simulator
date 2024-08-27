#!/usr/bin/env python
import struct
import socket
from dataclasses import dataclass

@dataclass 
class Element:
    x: float
    y: float
    z: float
array = []

loopback = "127.0.0.1"

for x in range(10):
    array.append(Element(10.6, 10.7, 10.8))

#Note that this array is 10 elements x 3 floats x 4 bytes = 120 bytes
print(array)

to_send = bytes()
#for i in range(len(array)):
for item in array:
    to_send += struct.pack('3f', item.x, item.y, item.z)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    
    port = 40000
    
    sock.connect(("127.0.0.1", port))
    
    sock.send(to_send)
