# oresat-simulator

The goal is to receive data (the outputs from a Basilisk simulation or similar) 
repeatedly via socket and then transmit that data repeatedly over serial port
to the Helmholtz Cage and Solar Simulator.

sock_ser_model contains the current server/client model. 

# Running the server and client
You should install GTK Terminal or the equivalent and open it with sudo:
For me using GTK:
sudo gtkterm -p /dev/ttyUSB1

Open s2s_server.py:
sudo ./s2s_server.py -IP [IP Address, default is 127.0.0.1]

Open s2s_client.py:
./s2s_client.py -IP [IP Address, default same as above]

When using two computers, use -IP [the IP address of the computer running
the server]
