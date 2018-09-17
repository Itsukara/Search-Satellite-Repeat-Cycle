from flask import Flask
#from flask import request
from flask import Response

#app = Flask(__name__)

### micro-utility for flask
def p0():
    global lines
    lines = ""
    
def p(l):
    global lines
    lines += str(l) + "\n"

def pn(l):
    global lines
    lines += str(l)

def r():
    return Response(lines, mimetype="text/plain")

def get_args(request, names):
    ns = names.split(",")
    r  = []
    for n in ns:
        if n in request.args:
            r.append(request.args[n])
        elif n in request.form:
            r.append(request.form[n])
        else:
            r.append("")
    return r

### body

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
def searchRepeatCycle(TLE, dt, maxlat, maxlong, maxdays, maxlongKm):
    # Initial Date
    dt0 = dt

    # Calculate Initial Ephemeris
    (line1, line2, line3) = TLE.split("\n")[0:3]
    satellite = ephem.readtle(line1, line2, line3)
    (latitude0, longitude0, hight0, mmotion0, obperiod0) = getEphem(satellite, dt)

    # Search Repeat Cycle
    eps      = obperiod0 / 360 / 10
    latKm   = 40009 # Circumference - meridional [Km]
    longKm  = 40075 # Circumference - quatorial  [Km]

    dt = dt0
    p("                                        Lat(+N)  diff[deg]   diff[Km] |   Long(+E)  diff[deg]   diff[Km]")
    for d in range(int(maxdays * mmotion0)):
      (latitude, longitude, _, _, _) = getEphem(satellite, dt)
      difflat   = latitude  - latitude0
      difflong  = longitude - longitude0

      if abs(difflat) < maxlat and abs(difflong) <maxlong:
        dtstr =jday2str(dt)
        days  = dt - dt0
        difflatKm  = difflat  / 360 * latKm
        difflongKm = difflong / 360 * longKm * math.cos(math.radians(latitude))
        p("[%s = %6.2f(days)] %10.4f %+10.4f %+10.4f | %10.4f %+10.4f %+10.4f" % (dtstr, days, latitude, difflat, difflatKm, longitude, difflong, difflongKm))
        if abs(difflongKm) > 0.001 and abs(difflongKm) < maxlongKm:
            p("*** Found Repeat Cycle (Long diff[Km] < " + str(maxlongKm) + ")")
            break

      # update dt
      dt = lat0date(satellite, dt + obperiod0, latitude0, eps)

CSKTLE = '''COSMO-SKYMED 4          
1 37216U 10060A   18258.17806865 -.00000011  00000-0  51372-5 0  9997
2 37216  97.8902  80.4717 0001356  76.0322 284.1025 14.82152713425139'''

#@app.route('/', methods=['GET', 'POST'])
#def ephem_test():
def ephem_test(request):
    p0()

    (TLE, date, maxlat, maxlong, maxdays, maxlongKm) = get_args(request, "TLE,date,maxlat,maxlong,maxdays,maxlongKm")
    TLE = TLE or CSKTLE
    TLE = TLE.replace("\r\n", "\n") if "\r\n" in TLE else TLE
    dt  = ephem.Date(date) if date else ephem.now()
    
    # Search Condition
    maxlat    = float(maxlat)  if maxlat  else 1.0 # max error of latitude[deg]
    maxlong   = float(maxlong) if maxlong else 1.0 # max error of longitude[deg]
    maxdays   = float(maxdays) if maxdays else 120 # max days of search
    maxlongKm = float(maxlongKm) if maxlongKm else 10.0 # max Long diff[Km]

    '''comment
    pn("TLE  ="); p(TLE)
    pn("date ="); p(date)
    pn("dt   ="); p(dt)
    pn("maxlat  ="); p(maxlat)
    pn("maxlong ="); p(maxlong)
    pn("maxdays ="); p(maxdays)
    pn("maxlongKm ="); p(maxlongKm)
    return r()
   '''

    p(TLE + "\n")
    searchRepeatCycle(TLE, dt, maxlat, maxlong, maxdays, maxlongKm)
    return r()

'''
@app.route('/hello', methods=['GET', 'POST'])
def hello_world():
    p0()
    pn("request.method="); p(request.method)
    pn("request.args  ="); p(request.args)
    pn("request.form  ="); p(request.form)
 
    (TLE, date) = get_args(request, "TLE,date")
    pn("TLE ="); p(TLE)
    pn("date="); p(date)
    
    return r()
'''