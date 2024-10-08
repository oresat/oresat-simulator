# oresat-simulator
Function: Take output data from client program and send it via socket to server program
which then transmits it over serial port to a hardware simulator. This model is currently
configured to send magnetometer data to the Helmholtz Cage.

# Dependencies Installation
Python
Basilisk
Pyserial

Start by installing Basilisk in a Python virtual environment.
Installing basilisk is complicated. Follow the instructions on:
https://hanspeterschaub.info/basilisk/Install/installOnLinux.html

Note that Basilisk has several dependencies which need to be installed first.

You will need to install pyserial within the virtual environment that you run Basilisk in.

Install with: "pip install pyserial"

If you cannot run this as root, you'll need to install it system-wide with your package manager. 
On Debian: "sudo apt install python3-pyserial"

#Permissions
In order to let the program access the computer's serial ports you may
need to set permissions:
sudo usermod -a -G dialout [username]

# Running the Server and Client
You need to be in a virtual environment for the files using Basilisk to function:
Venv recommended.

Activate your virtual environment.

In sock-ser-official:

Open server.py:
./server.py

Open scenarioMagneticFieldWMM.py
./scenarioMagneticFieldWMM.py

If you run with visualization the program will not send data until
the visualization windows are manually exited.

Quit with ctrl-c.
