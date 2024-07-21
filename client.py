import socket

sObj = socket.socket()

port = 12345

sObj.connect(('127.0.0.1', port))

print(sObj.recv(1024).decode())

sObj.close()
