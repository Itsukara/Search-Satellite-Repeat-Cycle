
# coding: utf-8

# # Search Repeat Cycle of Satellite from its TLE
# ## Satellite must be polar orbit

# In[1]:


import ephem


# In[2]:


# Two Line Element
line1 = "WORLDVIEW-1 (WV-1)"
line2 = "1 32060U 07041A   18258.02295190  .00000790  00000-0  35109-4 0  9993"
line3 = "2 32060  97.3879  16.4069 0002228  57.6683  54.8987 15.24397549611548"
satellite = ephem.readtle(line1, line2, line3)


# In[3]:


# Get Ephemeris Data
def getEphem(satellite, date):
  satellite.compute(date)
  latitude  = satellite.sublat / ephem.degree
  longitude = satellite.sublong / ephem.degree
  hight     = satellite.elevation
  mmotion   = satellite._n
  obperiod  = 1 / mmotion
  return (latitude, longitude, hight, mmotion, obperiod)


# In[4]:


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


# In[5]:


# Check Latitude is less than 45
dt  = ephem.Date("2018-09-18 10:35:01")

(latitude, longitude, hight, mmotion, obperiod) = getEphem(satellite, dt)
print("Lat(+N):%.4f, Long(+E):%.4f, Hight(m):%.1f, MeanMotion(RevPerDay):%.8f, OrbitalPeriod(days):%.8f" % (latitude, longitude, hight, mmotion, obperiod))

dt00 = dt
latitude0  = latitude
longitude0 = longitude
mmotion0   = mmotion
obperiod0  = obperiod


# In[6]:


# Search Repeat Cycle
eps      = obperiod / 360 / 10
maxlat   = 1.0 # max error of latitude[deg]
maxlong  = 1.0 # max error of longitude[deg]
maxdays  = 190 # max days of search

latlen   = 40009 # Circumference - meridional [Km]
longlen  = 40075 # Circumference - quatorial  [Km]

dt = dt00
print("Repeat Cycle of " + satellite.name)
print("                                         Lat(+N) diff[deg]   diff[Km] |   Long(+E)  diff[deg]   diff[Km]")
for d in range(int(maxdays * mmotion0)):
  (latitude, longitude, _, _, _) = getEphem(satellite, dt)
  difflat   = latitude  - latitude0
  difflong  = longitude - longitude0
  
  if abs(difflat) < maxlat and abs(difflong) <maxlong:
    dtstr= str(ephem.localtime(ephem.Date(dt)))[0:19]
    days = dt - dt00
    difflatlen  = difflat  / 360 * latlen
    difflonglen = difflong / 360 * longlen
    print("[%s = %6.2f(days)] %10.4f %+10.4f %+10.4f | %10.4f %+10.4f %+10.4f" % (dtstr, days, latitude, difflat, difflatlen, longitude, difflong, difflonglen))

  # update dt
  dt = lat0date(satellite, dt + obperiod, latitude0, eps)

