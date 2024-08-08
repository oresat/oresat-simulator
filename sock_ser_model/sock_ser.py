#!/usr/bin/env python
import serial
import socket
import time

#TO DO
#Put the socket stuff in a with block so that it opens with with (then
#it'll close automatically)

"""
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

while True:
    cSock, cAddr = sock.accept()

    with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
        try:
            while True:
                data = cSock.recv(4096) + b"\n\r"
                scribe = ser.write(data) #Ask the scribe to return the msg
                """
                Check if socket is still connected.
                """
                try:     
                    is_socket_open = cSock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
                    if len(is_socket_open) == -1:
                        print("\nSocket closed on other end. Will keep listening.\n")
                        break
                    elif len(is_socket_open) == 0:
                        print("\nSocket shut down in orderly fashion.\n")
                        break
                    elif len(is_socket_open) == 0:
                        print("\nABOVE ZERO\n")
                except BlockingIOError: #This is not a problem error.
                    pass

        except KeyboardInterrupt:
            print("\nEnded via ctrl-c.\n") 

