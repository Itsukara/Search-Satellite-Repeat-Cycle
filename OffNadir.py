import ephem
from pyorbital import orbital
import datetime
from math import asin, cos

# Sample Program to search pass and OffNadir of AOI

# Parameters
DEBUG = False
R = 6378.1 # Earth Radius
MaxOffNadir = "45.0" # Upper Limit of off-nadir angle
MaxPass = 5 # Number of passes to search

# Utility functions
def deg(radians):
    return radians / ephem.degree

def jday2datetime(jday):
    (year, month, day, hour, minute, second) = ephem.Date(jday).tuple()
    second = int(second)
    return datetime.datetime(year, month, day, hour, minute, second)

# Class for AOI
class AOI(ephem.Observer):
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.date = datetime.datetime.now()
        self.elevation = 0
        self.horizon = "00:00:00"

    def __str__(self):
        line = "*** AOI (%s)\n" % (self.name)
        a = self
        line += "Lat=%s (%.4f), Lon=%s (%.4f), Date=%s" % (a.lat, deg(a.lat), a.lon, deg(a.lon), a.date)
        return line

# Class for sat Information
class SatInfo:
    def __init__(self, tle, orbitOffset):
        self.tle = tle
        self.orbitOffset = orbitOffset
        (name, line1, line2) = tle.split("\n")[0:3]
        name = name.strip()
        line1 = line1.strip()
        line2 = line2.strip()
        self.name = name
        self.line1 = line1
        self.line2 = line2
        yyyy = "20" + line1[18:20]
        yday = line1[20:32]
        self.epoch = ephem.Date(ephem.Date(yyyy + "/1/1") + float(yday) - 1.0)
        # For ephem
        self.sat = ephem.readtle(name, line1, line2)
        # For pyorbital (to get orbit number)
        self.osat = orbital.Orbital(name, line1=line1, line2=line2)

    def __str__(self):
        s = self
        line = "*** TLE (name=%s, epoch=%s, orbitOffset=%s)\n" % (s.name, s.epoch, s.orbitOffset)
        line += s.tle
        return line

# Set Observer of sat

def searchPass(aoi, satInfo):
    # Print settings
    print(aoi)
    print("")
    print(satInfo)
    print("")
    print("*** Search Parameters")
    print("MaxOffNadir=%s" % (MaxOffNadir))
    print("MaxPass=%s" % (MaxPass))
    print("")

    # Search Pass not in Earth's shadow and off-nadir < MaxOffNadir
    print("*** Searching Passes")

    sat  = satInfo.sat
    osat = satInfo.osat
    orbitOffset  = satInfo.orbitOffset

    sat.compute(aoi)
    maxOffNadir = ephem.degrees(MaxOffNadir)
    i = 0
    while i < MaxPass:
        (rt, ra, mat, ma, st, sa) = aoi.next_pass(sat)
        #rt  Rise time
        #ra  Rise azimuth
        #mat Maximum altitude time
        #ma  Maximum altitude
        #st  Set time
        #sa  Set azimuth

        # Move sat to Max Alt Time
        aoi.date = mat
        sat.compute(aoi)

        # Compute off-nadir angle
        alt = sat.alt
        h = sat.elevation / 1000
        offNadir = ephem.degrees(asin(R/(R+h) * cos(alt)))
        eclipsed = sat.eclipsed
        if DEBUG:
            print("Max Alt=%4.1f[deg], Hight=%8.3fKm, OffNadir=%4.1f[deg], Eclipsed=%s" % (deg(alt), h, deg(offNadir), eclipsed))
        if offNadir < maxOffNadir and not eclipsed:
            i = i + 1
            orbit = osat.get_orbit_number(jday2datetime(mat)) + orbitOffset
            print("")
            '''\
            print("Rise    time=%s, Rise Az=%5.1f[deg]" % (rt, deg(ra)))
            print("Max Alt time=%s, Max Alt=%5.1f[deg], OffNadira=%4.1f[deg]" % (mat, deg(ma), deg(offNadir)))
            print("Set     time=%s, Set Az =%5.1f[deg]" % (st, deg(sa)))
            print("")
            #'''
            print("*** PASS # %d" % (i))
            print("AOI %s" % (aoi.name))
            print("Orbit     %20d" % (orbit))
            print("Datetime  %20s" % (mat))
            print("Latitude  %15s(+N)" % (sat.sublat))
            print("Longitude %15s(+E)" % (sat.sublong))
            print("Height    %15.1f[Km]"  % (sat.elevation / 1000))
            print("Azimuth  from AOI  %6.1f[deg]" % (deg(sat.az)))
            print("Altitude from AOI  %6.1f[deg]" % (deg(sat.alt)))
            print("Distance from AOI  %6.1f[Km]"  % (sat.range / 1000))
            print("Off-Nadir of AOI   %6.1f[deg]" % (deg(offNadir)))
        # Move sat to end of pass + 1 sec.
        aoi.date = st + ephem.second
        sat.compute(aoi)

    print("")
    print("*** Finished")

if __name__ == "__main__":
    AOIs = [["東京", "35.681452", "139.767042"],
            ["札幌", "43.068883", "141.350731"],
            ["博多", "33.590615", "130.420668"],
            ["ソウル", "37.555231", "126.970768"],
            ["那覇", "26.214471", "127.679391"],
            ["石垣", "24.340968", "124.155563"],
            ["北京", "39.916859", "116.397058"],
            ["ニューデリー", "28.641920", "77.221712"],
            ]

    TLE = '''WORLDVIEW-4 (WV-4)      
1 41848U 16067A   18272.22047166  .00000014  00000-0  78917-5 0  9995
2 41848  97.9049 348.6036 0000285  16.8379 343.2845 14.84975824101861'''

    satInfo = SatInfo(TLE, 2)
    for (name, lat, lon) in AOIs:
        aoi = AOI(name, lat, lon)
        searchPass(aoi, satInfo)
        print("***********************************")
