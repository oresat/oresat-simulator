#!/usr/bin/env python
import serial
import socket
import time
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Socket to serial TCP server."
    )

    parser.add_argument(
        "-IP", help="127.0.0.1 is loopback address",
        default="127.0.0.1"
    )

    args = parser.parse_args()

    """
    Ask the OS for a socket.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        """Create a port integer."""
        port = 16327
        
        """
        Bind the socket to our port.
        127.0.0.1 is the loopback host (means we connect to our computer).
        """
        sock.bind((args.IP, port))
        sock.listen()

        while True:
            cSock, cAddr = sock.accept()

            with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
                try:
                    while True:
                        data = cSock.recv(4096) 
                        dataAmount = len(data) #in bytes
                        if dataAmount == -1:
                            print("\nSocket closed on other end. Will keep listening.\n")
                            break
                        elif dataAmount == 0:
                            print("\nSocket shut down in orderly fashion.\n")
                            break
                        elif dataAmount > 0:
                            print(f"\n{dataAmount} bytes received. We're good for now.\n")
                        scribe = ser.write(data + b"\r\n") #Ask the scribe to return the msg + /r/n

                except KeyboardInterrupt:
                    print("\nEnded via ctrl-c.\n") 




