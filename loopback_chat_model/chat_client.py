import socket

"""
Ask the OS for a socket.
How do I do UNSPEC??? INET enables IPv4 only.
SOCK_STREAM enables TCP only.
"""
sObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""Create a port integer."""
port = 16327

"""
Connect to an IP address on a specific port.
Connection will fail if there is no server listening on said port.
"""

"""Tracks failed connections."""
counter = int(0)

while True:
    try:
        sObj.connect(('127.0.0.1', port))
    except:
        print("Problem connecting.\n")
        counter += 1;
        if counter > 2:
            exit()
    else:
        print("Connection successful.\n")
    
    data = sObj.recv(4096) 
    toPrint = data.decode()
    print(toPrint)
    if toPrint == "END":
        sObj.close()
        break        


