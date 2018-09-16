import ephem

# Get Ephemeris Data
def getEphem(satellite, date):
  satellite.compute(date)
  latitude  = satellite.sublat / ephem.degree
  longitude = satellite.sublong / ephem.degree
  hight     = satellite.elevation
  mmotion   = satellite._n
  obperiod  = 1 / mmotion
  return (latitude, longitude, hight, mmotion, obperiod)

# Search date with Latitude = lat
# satellite: ephem object
# date: latitude must be near lat at specified date
# lat: target latitude
# eps : small enough value
def lat0date(satellite, date, lat, eps):
  d1 = date
  satellite.compute(d1)
  l1  = satellite.sublat / ephem.degree
 
  d2 = d1 + eps
  satellite.compute(d2)
  l2  =satellite.sublat / ephem.degree

  a = (l2 - l1) / eps
  b = l1 - a * d1

  dt   = (lat - b) / a
  
  return dt


import datetime
def jday2str(jday):
    (year, month, day, hour, minute, second) = ephem.Date(jday).tuple()
    second = int(second)
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return dt.isoformat().replace('T', ' ')


# TLE: TLE of satellite
# datestr: Initial date (string)
# maxlat: max error of latitude[deg]
# maxlong: max error of longitude[deg]
# maxdays: max days of search
import math
def searchRepeatCycle(TLE, datestr, maxlat, maxlong, maxdays):
    # Initial Date
    dt0 = dt = ephem.Date(datestr)

    # Calculate Initial Ephemeris
    (line1, line2, line3) = TLE.split("\n")
    satellite = ephem.readtle(line1, line2, line3)
    (latitude0, longitude0, hight0, mmotion0, obperiod0) = getEphem(satellite, dt)

    # Search Repeat Cycle
    eps      = obperiod0 / 360 / 10
    latlen   = 40009 # Circumference - meridional [Km]
    longlen  = 40075 # Circumference - quatorial  [Km]

    dt = dt0
    print("                                         Lat(+N) diff[deg]   diff[Km] |   Long(+E)  diff[deg]   diff[Km]")
    for d in range(int(maxdays * mmotion0)):
      (latitude, longitude, _, _, _) = getEphem(satellite, dt)
      difflat   = latitude  - latitude0
      difflong  = longitude - longitude0

      if abs(difflat) < maxlat and abs(difflong) <maxlong:
        dtstr =jday2str(dt)
        days  = dt - dt0
        difflatlen  = difflat  / 360 * latlen
        difflonglen = difflong / 360 * longlen * math.cos(math.radians(latitude))
        print("[%s = %6.2f(days)] %10.4f %+10.4f %+10.4f | %10.4f %+10.4f %+10.4f" % (dtstr, days, latitude, difflat, difflatlen, longitude, difflong, difflonglen))

      # update dt
      dt = lat0date(satellite, dt + obperiod0, latitude0, eps)


# Search Repeat Cycle for each TLE and datestr
def searchRepeatCycles(TLEs, datestrs, maxlat, maxlong, maxdays):
    for TLE in TLEs:
        print("\n" + TLE + "\n")
        for datestr in datestrs:
            searchRepeatCycle(TLE, datestr, maxlat, maxlong, maxdays)
            print("")    
