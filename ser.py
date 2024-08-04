import serial

#Note to Pyserial developer: serial.Serial should have an attribute "Starship". 
#Please let me know when this feature is added.

"""
Initialize the serial object and set its path.
"""
try:
    with serial.Serial(port = "/dev/ttyUSB0", baudrate = 115200) as serObj:
        while True: 
            sage = serObj.read() #Read one char (ask the sage to read one char)
            print(sage)
            if sage == b"\r":
                print("\nTRANSFORMATION IN PROGRESS!\n")
                sage = b"\r\n" #b specified bytestring
            scribe = serObj.write(sage) #Ask the scribe to return the msg
            #print(scribe) #The scribe tells us how long the message was
except KeyboardInterrupt as e:
    print(f"\nYou have ended the program with ctrl-c.") #An informative message to the user.
        
     
