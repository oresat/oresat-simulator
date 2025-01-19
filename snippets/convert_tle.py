
from datetime import datetime
from sgp4.api import Satrec, jday


now = datetime.now()
jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

with open("tle.txt", "r") as fd:
    lines = fd.readlines()
    tle1 = lines[0]
    tle2 = lines[1]

satellite = Satrec.twoline2rv(tle1, tle2)
e, r, v= satellite.sgp4(jd, fr)

r = [element*1000 for element in r]
v = [element*1000 for element in v]

print(r)
print(v)

