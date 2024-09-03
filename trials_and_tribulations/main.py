import parse_tle
import numpy as np
"""This is used for checking the TLE parsing function"""

def main():
    # change text file tite to desired file. must be 2 line TLE
    file = "tle.txt"
    print(file)
    tle = parse_tle.Tle(file)
    tle._parse_tle()

    # uncomment to print all values
    #tle.display()

if __name__ == '__main__':
    main()