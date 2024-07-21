import socket

sObj = socket.socket()

#socket.socket(socket.AF_PASSIVE, socket.SOCK_STREAM)

port = 12345

sObj.bind(('127.0.0.1', port))

print(f"Socket bound to {port}.")

while True:
    c, addr = sObj.accept()
    print(f"Got connection from {addr}.")
    
    c.send("Thank you for connecting.".encode())
    
    c.close()
    
    break
