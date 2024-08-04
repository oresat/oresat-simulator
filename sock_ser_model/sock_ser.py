import serial
import socket

#Note to Pyserial developer: serial.Serial should have an attribute "Starship". 
#Please let me know when this feature is added.

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

data = cSock.recv(4096) 
    
"""
Initialize the serial object and set its path.
"""
with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as ser:
    scribe = ser.write(data) #Ask the scribe to return the msg

        
