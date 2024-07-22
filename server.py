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
Bind the socket to our port.
127.0.0.1 is the loopback host (means we connect to our computer).
Note that nothing is connected yet - just setting things up.
"""
try:
    sObj.bind(('127.0.0.1', port))
except:
    print(f"Error binding socket to port.")
    #print(sObj.gaierror()) #This line might be wrong.
    exit()
else:
    print(f"Socket bound to port: {port}.")

"""
Listen for incoming connections.
When found, accept the client.
Arg is 0 because there shouldn't be any unaccepted connections
before we connect to backlog (our own computer).
"""
while True:
    try: 
        sObj.listen(0)
    except:
        print("La la la la la, not listening!\n")
        #print(sObj.gaierror()) #I think there's a different error check method for this.
        exit()
    else:
        print("Listening...\n")
    
    #Connection is a new socket obj, address is that bound to socket on client side.
    try:
        connectedSocket, clientAddress = sObj.accept()
    except: 
        print("Did not accept.\n")
        #print(sObj.gaierror()) #Maybe?
        exit()
    else:
        print(f"Got connection from {clientAddress}.")
    
    #Send data over the socket. 
    msg = "Message received!"
    try:
        connectedSocket.send(msg.encode())
    except:
        print("Error sending.")
        #print(connectedSocket.gaierror()) #Maybe?
        exit()
    else:
        print("Message sent!")
    
    connectedSocket.close()
    
    break




