import Search_Satellite_Repeat_Cycle as ssrc

# INPUT DATA
# Two Line Element
TLE1 = '''WORLDVIEW-1 (WV-1)
1 32060U 07041A   18258.02295190  .00000790  00000-0  35109-4 0  9993
2 32060  97.3879  16.4069 0002228  57.6683  54.8987 15.24397549611548'''

TLE2 = '''WORLDVIEW-1 (WV-1)      
1 32060U 07041A   18258.81766689  .00000958  00000-0  41975-4 0  9990
2 32060  97.3884  17.1911 0002170  64.8045  86.2416 15.24400435611664'''

TLEs = (TLE1, TLE2)

# dates to search
datestrs = ("2018-09-18 10:46:01", "2018-09-18 10:41:01", "2018-09-18 10:36:01")

# Search Condition
maxlat   = 1.0 # max error of latitude[deg]
maxlong  = 1.0 # max error of longitude[deg]
maxdays  = 180 # max days of search

ssrc.searchRepeatCycles(TLEs, datestrs, maxlat, maxlong, maxdays)

