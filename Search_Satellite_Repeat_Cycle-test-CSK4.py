import Search_Satellite_Repeat_Cycle as ssrc

# INPUT DATA
# Two Line Element
TLE1 = '''COSMO-SKYMED 4          
1 37216U 10060A   18258.17806865 -.00000011  00000-0  51372-5 0  9997
2 37216  97.8902  80.4717 0001356  76.0322 284.1025 14.82152713425139'''

TLEs = (TLE1,)

# dates to search
datestrs = ("2018-09-17 00:39:00",)

# Search Condition
maxlat   = 1.0 # max error of latitude[deg]
maxlong  = 1.0 # max error of longitude[deg]
maxdays  =  80 # max days of search

ssrc.searchRepeatCycles(TLEs, datestrs, maxlat, maxlong, maxdays)

