#!/usr/bin/env python
import serial
import socket
import argparse

#See README for argparse instructions.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Socket to serial TCP server."
    )

    parser.add_argument(
        "-IP", action="store_true", help="127.0.0.1 is loopback address",
        default="127.0.0.1"
    )

    parser.add_argument(
        "-TERM", action="store_false", help="Run program as terminal, for testing"
    )   

    args = parser.parse_args()

    #Ask the OS for a socket.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        #Create a port integer.
        port = 16327
        
        #Bind the socket to our port.
        sock.bind((args.IP, port))
        sock.listen()

        while True:
            #Accept an incoming client with a copy of sock.
            cSock, cAddr = sock.accept()

            #Open up one end of serial port, set data transfer rate.
            with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
                if args.TERM:    
                    try:
                        #Continuously attempt to receive data via socket from client.
                        #If nothing bad happens, scribe sends
                        #the received data over the serial port.
                        while True:
                            data = cSock.recv(4096) 
                            dataAmount = len(data) #in bytes
                            if dataAmount == 0:
                                print("\nSocket shut down in orderly fashion.\n")
                                break
                            elif dataAmount > 0:
                                print(f"\n{dataAmount} bytes received. We're good for now.\n")
                            scribe = ser.write(data + b"\r\n") #Scribe returns the msg + /r/n

                    except KeyboardInterrupt:
                        print("\nEnded via ctrl-c.\n") 
                else:
                    try:
