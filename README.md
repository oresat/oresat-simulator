# oresat-simulator

The goal is to receive data (the outputs from a Basilisk simulation or similar) 
repeatedly via socket and then transmit that data repeatedly over serial port
to the Helmholtz Cage and Solar Simulator.

sock_ser_model contains the current server/client model. 

# Dependencies Installation
pyserial

Install with: pip install pyserial might work
If cannot run this as root, you'll need to install it system-wide 
with your package manager. 
On Debian: "sudo apt install python3-pyserial"

#Permissions
In order to let the program access the computer's serial ports you may
need to set permissions:
sudo usermod -a -G dialout [root_username]

# Running the server and client
You need to be in a virtual environment for the files using Basilisk to function:
Venv recommended.

You should install GTK Terminal or the equivalent and open it with sudo:
For me using GTK:
sudo gtkterm -p /dev/ttyUSB1

Activate your virtual environment.

In trials_and_tribulations:

Open server.py:
./server.py

Open scenarioMagneticFieldWMM.py
./scenarioMagneticFieldWMM.py

If you run with visualization the program will not send data until
the visualization windows are manually exited.

Quit with ctrl-c.
