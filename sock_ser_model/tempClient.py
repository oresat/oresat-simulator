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

def pack_array_data(array):
    for x in range(10):
        array.append(Element(10.6, 10.7, 10.8))

    to_send = bytes()
    #for i in range(len(array)):
    for item in array:
        to_send += struct.pack('3f', item.x, item.y, item.z)
    return to_send 

pack_array_data(array)
print(array)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    
    port = 40000
    
    sock.connect(("127.0.0.1", port))
   
    sock.send(to_send)
