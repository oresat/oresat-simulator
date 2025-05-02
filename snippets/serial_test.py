
import time
import serial

connected = False
while not connected:
    try:
        ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=5)
        connected = True
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    except:
        print("waiting for serial port")

time.sleep(1)
for i in range(20):
    s = ser.read_until()
    print(s)
    time.sleep(0.1)
    if s == b'':
        break



# do control c
ser.write(b'\x03')
time.sleep(1)
for i in range(20):
    s = ser.read_until()
    print(s)
    time.sleep(0.1)
    if s == b'':
        break

# do control d
ser.write(b'\x04')
time.sleep(1)
for i in range(20):
    s = ser.read_until()
    print(s)
    time.sleep(0.1)
    if s == b'':
        break


 
# accept first argument
ser.write('\r\n'.encode('utf-8'))
time.sleep(1)
for i in range(20):
    s = ser.read_until()
    print(s)
    time.sleep(0.1)
    if s == b'':
        break


  
ser.write('3\r'.encode('utf-8'))
for i in range(20):
    s = ser.read_until()
    print(s)
    time.sleep(0.1)
    if s == b'':
        break

ser.write('3\r'.encode('utf-8'))
for i in range(20):
    s = ser.read_until()
    print(s)
    time.sleep(0.1)
    if s == b'':
        break

 
ser.write('0\r'.encode('utf-8'))
