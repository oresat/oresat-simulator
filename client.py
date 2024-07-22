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
while True:
    try:
        sObj.connect(('127.0.0.1', port))
    except:
        print("Problem connecting.\n")
    else:
        print("Connection successful.\n")
    
    data = sObj.recv(4096) 
    print(data.decode())

    sObj.close()
    
    break
