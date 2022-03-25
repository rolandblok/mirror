import time, math

# https://stackoverflow.com/questions/8708048/position-of-the-sun-given-time-of-day-latitude-and-longitude
def sunPosition(lat=51.441642, long=5.4697225, in_degrees=True):
    # Latitude [rad]
    lat_rad = math.radians(lat)

    # Get Julian date - 2400000
    day = time.gmtime().tm_yday
    hour = time.gmtime().tm_hour + \
           time.gmtime().tm_min/60.0 + \
           time.gmtime().tm_sec/3600.0
    delta = time.gmtime().tm_year - 1949
    leap = delta / 4
    jd = 32916.5 + delta * 365 + leap + day + hour / 24
    # print ("year   {}".format(time.gmtime().tm_year))
    # print ("yday   {}".format(time.gmtime().tm_yday))
    # print ("hour   {}".format(time.gmtime().tm_hour))
    # print ("minute {}".format(time.gmtime().tm_min))
    # print ("second {}".format(time.gmtime().tm_sec))
    # print ("cur_hr   {}".format(hour))
    # print ("leap   {}".format(leap))
    # print ("delta   {}".format(delta))
    # print ("jd {}".format(jd))

    # The input to the Atronomer's almanach is the difference between
    # the Julian date and JD 2451545.0 (noon, 1 January 2000)
    t = jd - 51545

    # Ecliptic coordinates

    # Mean longitude
    mnlong_deg = (280.460 + .9856474 * t) % 360

    # Mean anomaly
    mnanom_rad = math.radians((357.528 + .9856003 * t) % 360)

    # Ecliptic longitude and obliquity of ecliptic
    eclong = math.radians((mnlong_deg + 
                           1.915 * math.sin(mnanom_rad) + 
                           0.020 * math.sin(2 * mnanom_rad)
                          ) % 360)
    oblqec_rad = math.radians(23.439 - 0.0000004 * t)

    # Celestial coordinates
    # Right ascension and declination
    num = math.cos(oblqec_rad) * math.sin(eclong)
    den = math.cos(eclong)
    ra_rad = math.atan(num / den)
    if den < 0:
        ra_rad = ra_rad + math.pi
    elif num < 0:
        ra_rad = ra_rad + 2 * math.pi
    dec_rad = math.asin(math.sin(oblqec_rad) * math.sin(eclong))

    # Local coordinates
    # Greenwich mean sidereal time
    gmst = (6.697375 + .0657098242 * t + hour) % 24
    # Local mean sidereal time
    lmst = (gmst + long / 15) % 24
    lmst_rad = math.radians(15 * lmst)

    # Hour angle (rad)
    ha_rad = (lmst_rad - ra_rad) % (2 * math.pi)

    # Elevation
    el_rad = math.asin(
        math.sin(dec_rad) * math.sin(lat_rad) + \
        math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad))

    # Azimuth
    az_rad = math.asin(
        - math.cos(dec_rad) * math.sin(ha_rad) / math.cos(el_rad))

    if (math.sin(dec_rad) - math.sin(el_rad) * math.sin(lat_rad) < 0):
        az_rad = math.pi - az_rad
    elif (math.sin(az_rad) < 0):
        az_rad += 2 * math.pi

    if in_degrees:
        return el_rad*180/math.pi, az_rad*180/math.pi
    else:
        return el_rad, az_rad


# https://itk.org/files/Examples/src/Core/Transform/CartesianToAzimuthElevation/Documentation.html
def xyz2elaz(x,y,z):
    azimuth = math.arctan(x/y)
    elevation = math.arctan(y/z)
    return (elevation, azimuth)

import calendar

if __name__ == '__main__':
    print (calendar.timegm(time.gmtime()))
    print(sunPosition())