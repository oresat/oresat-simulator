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
        "-IP", help="127.0.0.1 is loopback address",
        default="127.0.0.1"
    )

    args = parser.parse_args()

    #Ask the OS for a socket.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        @dataclass 
        class Element:
            x: float
            y: float
            z: float
        array = []

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
                try:
                    while True:
                        data = cSock.recv(120) 
                        dataAmount = len(data) #in bytes
                        if dataAmount == 0:
                            print("\nSocket shut down in orderly fashion.\n")
                            break
                        elif dataAmount > 0:
                            print(f"\n{dataAmount} bytes received. We're good for now.\n")
                        scribe = ser.write(data + b"\r\n") #Scribe returns the msg + /r/n
                        #array.append(element(data.decode(python struct 4 bytes)))  
    
                        

                except KeyboardInterrupt:
                    print("\nEnded via ctrl-c.\n") 
