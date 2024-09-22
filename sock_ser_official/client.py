#!/usr/bin/env python
#OUTDATED, use scenarioMagnetic... .py
import struct
import socket
from dataclasses import dataclass
import pprint
import time

array = []

loopback = "127.0.0.1"
x = 1.5
y = 2.5
z = 3.5

def pack_array_data(array):
    for a in range(10):
        array.append([x, y, z])

    to_send = bytes()
    #for i in range(len(array)):
    for item in array:
        for i in range(3):
            to_send += struct.pack('f', item[i])
    return to_send 

cargo = pack_array_data(array)
pprint.pp(array)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    port = 40000
    
    sock.connect(("127.0.0.1", port))
    try:
        while True: 
            sock.send(cargo) 
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nClient ended via ctrl-c.\n")
