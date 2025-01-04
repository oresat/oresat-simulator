
import numpy as np
import datetime as dt

class Tle(object):
    #Class holding TLE objects

    def __init__(self, tle_file):
        # set up all the things
        self.tle_file = tle_file
        self.line1 = None
        self.line2 = None

        self.satnumber = None
        self.classification = None
        self.id_launch_year = None
        self.id_launch_number = None
        self.id_launch_piece = None
        self.epoch_year = None
        self.epoch_day = None
        self.epoch = None
        self.mean_motion_derivative = None
        self.mean_motion_sec_derivative = None
        self.bstar = None
        self.ephemeris_type = None
        self.element_number = None
        self.inclination = None
        self.right_ascension = None
        self.excentricity = None
        self.arg_perigee = None
        self.mean_anomaly = None
        self.mean_motion = None
        self.orbit = None
        self.mu = None
        self.semimajor_axis = None
        self.true_anomaly = None
        self.perigee = None
        self.apogee = None

        self._read_tle()
        self._checksum()
        self._parse_tle()

    def _checksum(self):
        # Calculate checksum for the current TLE
        for line in [self.line1, self.line2]:
            check = 0
            for char in line[:-1]:
                if char.isdigit():
                    check += int(char)
                if char == "-":
                    check += 1

            if (check % 10) != int(line[-1]):
                raise KeyError(self.tle_file + " " + line)

    def _read_tle(self):
        # Read TLE data from a file
        with open(self.tle_file, 'r') as f:
            lines = f.read().splitlines()
        
        self.line1 = lines[0]
        self.line2 = lines[1]

        if self.line1 is not None and self.line2 is not None:
            tle = self.line1.strip() + "\n" + self.line2.strip()
        else:
                raise KeyError("Found no TLE entry for '%s'" % self.tle_file)

        self.line1, self.line2 = tle.split('\n')

    def _parse_tle(self):
        # Parsing values (based on character location which isn't really the best way - intend to change later)
        def _read_tle_decimal(rep):
            # Convert *rep* to decimal value
            if rep[0] in ["-", " ", "+"]:
                digits = rep[1:-2].strip()
                val = rep[0] + "." + digits + "e" + rep[-2:]
            else:
                digits = rep[:-2].strip()
                val = "." + digits + "e" + rep[-2:]

            return float(val)

        first_line = self.line1.split()
        second_line = self.line2.split()

        var = first_line[1]
        self.classification = var[-1]#self.line1[7]
        self.satnumber = var[:-1]

        var = first_line[2]
        self.id_launch_year = float(var[0:2])
        self.id_launch_number = float(var[2:-1])
        self.id_launch_piece = var[-1]

        var = first_line[3]
        self.epoch_year = var[0:2]
        self.epoch_day = float(var[2:])
        self.epoch = \
            np.datetime64(dt.datetime.strptime(self.epoch_year, "%y") +
                          dt.timedelta(days=self.epoch_day - 1), 'us')
        
        self.mean_motion_derivative = float(first_line[4])
        self.mean_motion_sec_derivative = _read_tle_decimal(first_line[5])
        self.bstar = _read_tle_decimal(first_line[6])
        try:
            self.ephemeris_type = int(first_line[7])
        except ValueError:
            self.ephemeris_type = 0
        self.element_number = int(first_line[8]) # ?????TODO FIXME?????

        self.inclination = float(second_line[2])
        self.right_ascension = float(second_line[3])
        self.excentricity = int(second_line[4]) * 10 ** -7
        self.arg_perigee = float(second_line[5])
        self.mean_anomaly = float(second_line[6])

        var = second_line[7]
        self.mean_motion = round(float(self.line2[52:63]), 4) ##hewp :(
        self.orbit = int(self.line2[63:68])

        self.mu = 398600.4418 #km^3 / s^2
        # semimajor axis includes the diameter of the earth, so a value under 7000km is expected
        self.semimajor_axis = round(((self.mu**(1/3)) / (((2*self.mean_motion*np.pi)/(86400))**(2/3))), 4)

        # true anomaly is a limit value, so calculated in a funky way
        M = self.mean_anomaly
        ECC_A = M
        for _ in range (10):
            ECC_A = M + (self.excentricity*np.sin(ECC_A))
        ECC_A = round(ECC_A, 5)
        beta = (1 - np.sqrt(1 - (self.excentricity ** 2))) / self.excentricity
        self.true_anomaly = round((ECC_A + 2*np.arctan((beta * np.sin(ECC_A)) / (1 - (beta * np.cos(ECC_A))))), 4)

        self.perigee = round(self.semimajor_axis * (1 - self.excentricity), 4)
        self.apogee = round(self.semimajor_axis * (self.excentricity + 1), 4)

    def display(self):
        # Just print everything for debugging reasons
        print(
        "\tline1:", self.line1, "\n",
        "\tline2:", self.line2, "\n",
        "sat num:", self.satnumber, "\n",
        "class:", self.classification, "\n",
        "Launch year:", self.id_launch_year, "\n",
        "launch num:", self.id_launch_number, "\n",
        "id:", self.id_launch_piece, "\n",
        "epoch year:", self.epoch_year, "\n",
        "epoch day:", self.epoch_day, "\n",
        "epoch:", self.epoch, "\n",
        "1st mean deriv:", self.mean_motion_derivative, "\n",
        "2nd mean deriv:", self.mean_motion_sec_derivative, "\n",
        "drag term:", self.bstar, "\n",
        "ephem type:", self.ephemeris_type, "\n",
        "element num:", self.element_number, "\n",
        "inclination:", self.inclination, "\n",
        "right ascend:", self.right_ascension, "\n",
        "excentricity:", self.excentricity, "\n",
        "arg of perigree:", self.arg_perigee, "\n",
        "mean anomaly:", self.mean_anomaly, "\n",
        "mean motion (rev/day):", self.mean_motion, "\n",
        "orbit (revolutions at epoch):", self.orbit, "\n",
        "mu:", self.mu, "\n",
        "semimajor axis:", self.semimajor_axis, "\n",
        "parigee:", self.perigee, "\n",
        "apogee:", self.apogee, "\n",
        "true anomaly:", self.true_anomaly)