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
def searchRepeatCycle(TLE, dt, maxlat, maxlong, maxdays):
    # Initial Date
    dt0 = dt

    # Calculate Initial Ephemeris
    (line1, line2, line3) = TLE.split("\n")[0:3]
    satellite = ephem.readtle(line1, line2, line3)
    (latitude0, longitude0, hight0, mmotion0, obperiod0) = getEphem(satellite, dt)

    # Search Repeat Cycle
    eps      = obperiod0 / 360 / 10
    latlen   = 40009 # Circumference - meridional [Km]
    longlen  = 40075 # Circumference - quatorial  [Km]

    lines = ""
    dt = dt0
#    print("                                         Lat(+N) diff[deg]   diff[Km] |   Long(+E)  diff[deg]   diff[Km]")
    lines += "                                         Lat(+N) diff[deg]   diff[Km] |   Long(+E)  diff[deg]   diff[Km]\n"
    for d in range(int(maxdays * mmotion0)):
      (latitude, longitude, _, _, _) = getEphem(satellite, dt)
      difflat   = latitude  - latitude0
      difflong  = longitude - longitude0

      if abs(difflat) < maxlat and abs(difflong) <maxlong:
        dtstr =jday2str(dt)
        days  = dt - dt0
        difflatlen  = difflat  / 360 * latlen
        difflonglen = difflong / 360 * longlen * math.cos(math.radians(latitude))
#        print("[%s = %6.2f(days)] %10.4f %+10.4f %+10.4f | %10.4f %+10.4f %+10.4f" % (dtstr, days, latitude, difflat, difflatlen, longitude, difflong, difflonglen))
        lines += "[%s = %6.2f(days)] %10.4f %+10.4f %+10.4f | %10.4f %+10.4f %+10.4f\n" % (dtstr, days, latitude, difflat, difflatlen, longitude, difflong, difflonglen)

      # update dt
      dt = lat0date(satellite, dt + obperiod0, latitude0, eps)
    
    return lines

from flask import Response
def ephem_test(request):
    TLE  = ""
    date = ""
    if request:
        request_json = request.get_json()
        if request.args:
            if 'TLE' in request.args:
                TLE  = request.args.get('TLE')
            if 'date' in request.args:
                date = request.args.get('date')
        elif request_json:
            if 'TLE' in request_json:
                TLE  = request_json['TLE']
            if 'date' in request_json:
                date = request_json['date']
        else:
            if 'TLE' in request.form:
                TLE  = request.form['TLE']
            if 'date' in request.form:
                date = request.form['date']
    if not TLE:
        TLE = '''COSMO-SKYMED 4          
1 37216U 10060A   18258.17806865 -.00000011  00000-0  51372-5 0  9997
2 37216  97.8902  80.4717 0001356  76.0322 284.1025 14.82152713425139'''
    if date:
        dt = ephem.Date(date)
    else:
        dt = ephem.now()
    
    maxlat   = 1.0 # max error of latitude[deg]
    maxlong  = 1.0 # max error of longitude[deg]
    maxdays  = 180 # max days of search
    text = TLE + "\n\n" + searchRepeatCycle(TLE, dt, maxlat, maxlong, maxdays)
    return Response(text, mimetype='text/plain')