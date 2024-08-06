#!/usr/bin/env python
import socket

#TO DO

"""
Ask the OS for a socket.
How do I do UNSPEC??? INET enables IPv4 only.
SOCK_STREAM enables TCP only.
"""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""Create a port integer."""
port = 16327

"""
Connect to an IP address on a specific port.
Connection will fail if there is no server listening on said port.
"""

sock.connect(('127.0.0.1', port))

try:
    while True:    
        msg = input("Enter text, good sir: ")

        sock.send(msg.encode())

except KeyboardInterrupt:
    print("\nEnded via ctrl-c.\n")










