Basilisk must be installed and functioning correctly to run these modules.

To run the mag field simulation, copy the desired TLE to the tle.txt file. Just the 2 lines of data, without the line that includes the satellite name.

To run:
    "./scenarioMagneticFieldWMM.py"

The program will print out a list of lists of magnetic field values, with each element
containing a vector [X,Y,Z] of coordinates (floats).

One orbit with 100 data points is the standard.

This data can be redirected to a file if desired.
