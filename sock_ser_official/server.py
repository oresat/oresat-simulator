#!/usr/bin/env python
import struct
import socket
from dataclasses import dataclass
import serial
import pprint

#Server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    port = 40000
    sock.bind(("127.0.0.1", port))
    sock.listen()
    try:
        while True:
            cSock, cAddr = sock.accept()
            while True:
                data = cSock.recv(1200) 
                dataAmount = len(data)
                if dataAmount == 0:
                    print("\nSocket shut down in orderly fashion.\n")
                    break
                elif dataAmount > 0:
                    print(f"\n{dataAmount} bytes received.\n")

                print("\nHere is the unpacked version that we'll send as bytes.\n")
                #using a list comprehension, appends automatically
                new_array = [[x,y,z] for x, y, z in struct.iter_unpack('3f', data)]
                pprint.pp(new_array)
                
                with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
                    print()
                    print(data.hex())
                    print()
                    envoy = ser.write(data)

    except KeyboardInterrupt:   
        print("\nEnded via ctrl-c. Goodbye!\n")
