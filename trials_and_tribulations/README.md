Basilisk must be installed and funcitoning correctly to run these modules. Refer to http://hanspeterschaub.info/basilisk/Install.html
for detailed installation instructions after the basilisk repo is pulled to a local repo.

To run the mag field simulation, copy the desired TLE to the tle.txt file. Just the 2 lines of data,
without the line that includes the satellite name.
To run:
    `./scenarioMagneticFieldWMM.py`
    or
    `python3 scenarioMagneticFieldWMM.py`

The program will print out a list of lists of magnetic field values, in the order of the X, Y, and Z axis.
One orbit with 100 data points is the standard.
This data can be redirected to a file if desired.
