#import parse_tle
#import numpy as np
"""This is used for checking the TLE parsing function"""

def T_to_mG(data):
    #convert each value to mG. 1Tesla = 10^7 mG
    mG_vals = []
    #with open(file, 'r') as file:
    #        lines = file.read().splitlines()

    for line in data:
        entry = line.split(" ")
        mG_line = []
        i = 0
        while i < len(entry):
            val = entry[i].strip("[]")
            if(val):
                val = float(val)
                format(val, '.12f')
                val = val * (10000000)
                val = round(val, 4)
                mG_line.append(val)

            i = i + 1

        mG_vals.append(mG_line)

    print(mG_vals)

def main():
    # change text file tite to desired file. must be 2 line TLE
    #file = "tle.txt"
    #print(file)
    #tle = parse_tle.Tle(file)
    #tle._parse_tle()

    #tle.display()

    #file = "magDataOresat0-aug20.txt"
    T_to_mG("[[ 5.0470977721333283e-08 -2.6219676806665417e-07  1.0918149679423498e-06] [ 1.2682939333686114e-07 -9.1233077683226458e-08  1.1171507266795166e-06] 2.0689497902296717e-07  8.0634116940838938e-08  1.1207188598264001e-06]]")

if __name__ == '__main__':
    main()