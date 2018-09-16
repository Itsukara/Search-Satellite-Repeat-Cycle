import ephem

#
# Sample Program to calculate satellite pass
#
# Observer = Mt. Fuji
mtfuji = ephem.Observer()
mtfuji.lon = "138.43:40.0"
mtfuji.lat =  "35:21:38.7"
mtfuji.elevation = 3776
mtfuji.horizon = "5:00:00"
#
# Satellite = WolrdView-1
#
TLE = '''WORLDVIEW-1 (WV-1)
1 32060U 07041A   18258.02295190  .00000790  00000-0  35109-4 0  9993
2 32060  97.3879  16.4069 0002228  57.6683  54.8987 15.24397549611548'''
(line1, line2, line3) = TLE.split("\n")
wv01 = ephem.readtle(line1, line2, line3)

# Set Observer of Satellite
wv01.compute(mtfuji)

# Print setting
print(TLE)
print("")
print("Observer=Mt. Fuji=%s" % (mtfuji))
print("")

# Search Pass not in Earth's shadow
MAXPASS = 20
i = 0
while i < MAXPASS:
    (rt, ra, mat, ma, st, sa) = mtfuji.next_pass(wv01)

    # Move Satellite to start of next pass
    mtfuji.date = rt
    wv01.compute(mtfuji)
#    print("Alt=%s, Az=%s" % (wv01.alt, wv01.az))

    if wv01.eclipsed:
#        print("*** Satelite is in Earth's shadow ***")
        pass
    else:
        i = i + 1
        print("PASS # %d" %(i))
        print("Rise    time=%s, Rise Az=%s" % (rt, ra))
        print("Max Alt time=%s, Max Alt=%s" % (mat, ma))
        print("Set     time=%s, Set  Az=%s" % (st, sa))
        print("")

    # Move Satellite to end of pass + 1 sec.
    mtfuji.date = st + ephem.second
    wv01.compute(mtfuji)
#    print("Alt=%s, Az=%s" % (wv01.alt, wv01.az))


