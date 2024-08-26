import struct
import socket
from dataclasses import dataclass

@dataclass 
class Element:
    x: float
    y: float
    z: float
array = []

#Server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    port = 40000
    sock.bind(("127.0.0.1", port))
    sock.listen()

    cSock, cAddr = sock.accept()

    data = cSock.recv(120) 

    array = struct.unpack('30f', data)

print(array)
print()

#Reformat array

new_array = [] 
length = len(array)
new_array_length = int(len(array) / 3)
print(new_array_length)
i = 0
h = 0

while h < new_array_length:
    Element = (array[i], array[i+1], array[i+2])
    print(f"Iteration {h} basically complete.")
    new_array.append(Element)
    i += 3
    h += 1

print(f"The reformatted array:\n{new_array}")
