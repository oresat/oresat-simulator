#This file is a test file for the Helmholtz crew to steal.
import struct
import serial
import pprint

#Open a serial port.
with serial.Serial(port = "/dev/ttyUSB1", baudrate = 115200) as ser:
    while True:
        #Continuously listen for incoming serial data.
        data = ser.read(1140)
        #If there is actual data that comes through:
        if len(data) > 0:
            #Unpack that data (will arrive in byte format) and make vectors.
            new_array = [[x,y,z] for x, y, z in struct.iter_unpack('3f', data)]
            #This line prints it to the terminal, for test purposes.
            pprint.pp(new_array)



