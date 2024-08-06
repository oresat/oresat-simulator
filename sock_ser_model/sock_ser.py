#!/usr/bin/env python
import serial
import socket

#TO DO
"""
Handle case where client closes (sock_ser should stay on the whole time) and then re-opens. Experiment.
Server can take in multiple clients sequentially.
Clean up comments, files, etc.
"""

"""
Ask the OS for a socket.
How do I do UNSPEC??? INET enables IPv4 only.
SOCK_STREAM enables TCP only.
"""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""Create a port integer."""
port = 16327

"""
Bind the socket to our port.
127.0.0.1 is the loopback host (means we connect to our computer).
Note that nothing is connected yet - just setting things up.
"""
sock.bind(('127.0.0.1', port))
sock.listen()
cSock, cAddr = sock.accept()


with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
    try:
        while True:
            data = cSock.recv(4096) + b"\n\r"
            scribe = ser.write(data) #Ask the scribe to return the msg

    except KeyboardInterrupt:
        print("\nEnded via ctrl-c.\n") 

