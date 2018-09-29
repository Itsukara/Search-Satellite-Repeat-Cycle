import ephem
from pyorbital import orbital
import datetime
from math import asin, cos

# Sample Program to search pass and OffNadir of AOI
DEBUG = True
R = 6378.1 # Earth Radius
MaxOffNadir = "45.0" # Upper Limit of off-nadir angle
MaxPass = 5 # Number of pass to search

# AOI / Obserber
AOI = ephem.Observer()
AOI.lon = "138:43:40.0"
AOI.lat =  "35:21:38.7"
AOI.elevation = 0
AOI.horizon = "00:00:00"

# Satellite TLE
TLE = '''WORLDVIEW-4 (WV-4)      
1 41848U 16067A   18272.22047166  .00000014  00000-0  78917-5 0  9995
2 41848  97.9049 348.6036 0000285  16.8379 343.2845 14.84975824101861'''
(line0, line1, line2) = TLE.split("\n")
line0 = line0.strip()

yyyy = "20" + line1[18:20]
yday = line1[20:32]
epoch = ephem.Date(ephem.Date(yyyy + "/1/1") + float(yday) - 1.0)

# Satellite of ephem
satellite = ephem.readtle(line0, line1, line2)

# Satellite of pyorbital (to get orbit number)
po_satellite = orbital.Orbital(line0, line1=line1, line2=line2)
OrbitOffset = 0 # Offset from orbit number of pyorbital

# Set Observer of Satellite
satellite.compute(AOI)

# Print setting
print("*** TLE (epoch=%s)" % (epoch))
print(TLE)
print("")
print("*** AOI")
print("lon=%s, lat=%s" % (AOI.lon, AOI.lat))
print("")
print("*** Search Parameters")
print("MaxOffNadir=%s" % (MaxOffNadir))
print("MaxPass=%s" % (MaxPass))
print("OrbitOffset=%d" % (OrbitOffset))
print("")

# Utility functions
def deg(radians):
    return radians / ephem.degree

def jday2datetime(jday):
    (year, month, day, hour, minute, second) = ephem.Date(jday).tuple()
    second = int(second)
    return datetime.datetime(year, month, day, hour, minute, second)

# Search Pass not in Earth's shadow and off-nadir < MaxOffNadir
print("*** Searching Passes")
print("")

MaxOffNadir = ephem.degrees(MaxOffNadir)
i = 0
while i < MaxPass:
    (rt, ra, mat, ma, st, sa) = AOI.next_pass(satellite)
    #rt  Rise time
    #ra  Rise azimuth
    #mat Maximum altitude time
    #ma  Maximum altitude
    #st  Set time
    #sa  Set azimuth

    # Move Satellite to Max Alt Time
    AOI.date = mat
    satellite.compute(AOI)

    # Compute off-nadir angle
    alt = satellite.alt
    h = satellite.elevation / 1000
    offNadir = ephem.degrees(asin(R/(R+h) * cos(alt)))
    eclipsed = satellite.eclipsed
    if DEBUG:
        print("Max Alt=%4.1f[deg], Hight=%8.3fKm, OffNadir=%4.1f[deg], Eclipsed=%s" % (deg(alt), h, deg(offNadir), eclipsed))
    if offNadir < MaxOffNadir and not eclipsed:
        i = i + 1
        orbit = po_satellite.get_orbit_number(jday2datetime(mat)) + OrbitOffset
        print("")
        print("PASS # %d, Orbit=%d" %(i, orbit))
        print("Rise    time=%s, Rise Az=%5.1f[deg]" % (rt, deg(ra)))
        print("Max Alt time=%s, Max Alt=%5.1f[deg], OffNadira=%5.1f[deg]" % (mat, deg(ma), deg(offNadir)))
        print("Set     time=%s, Set Az =%5.1f[deg]" % (st, deg(sa)))
        print("")

    # Move Satellite to end of pass + 1 sec.
    AOI.date = st + ephem.second
    satellite.compute(AOI)

print("")
print("*** Finished")