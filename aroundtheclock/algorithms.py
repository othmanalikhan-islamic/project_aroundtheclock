"""
Formulae used to compute prayer times.
"""


import datetime as dt
from math import acos, asin, atan, atan2, cos, degrees, radians, sin, tan

import julian


################################################# PRIVATE FUNCTIONS


def julianEquation(date):
    """
    Converts a Gregorian date to a Julian date.

    :param date: datetime.datetime, representing the Gregorian date.
    :return: Number, the corresponding Julian date.
    """
    return julian.to_jd(date)


def sunEquation(date):
    """
    Calculates the declination of the sun and the equation of time which are
    needed in prayer calculations. The equations below are approximations of
    the real values however with an error of 1 arc minute at worst in 2200.

    Definitions:
        Equation of Time = Apparent Solar Time - Mean Solar Time
        Declination = The angle between the sun's rays and Earth's equator.

    Abbreviations:
        d - Number of days and fraction from 2000 January 1.5 (J2000.0)
        g - Mean anomaly of the sun
        q - Mean longitude of the sun
        L - Geocentric apparent ecliptic longitude of the sun (adjusted for aberration)
        e - Mean obliquity of the ecliptic
        RA - Right ascension

    :param date: datetime.datetime, computing sun parameters for this date.
    :return: 2-Tuple, (declination, equation of time)
    """
    d = julianEquation(date) - 2451545.0

    g = radians((357.529 + 0.98560028 * d) % 360)
    q = radians((280.459 + 0.98564736 * d) % 360)
    L = radians((degrees(q) + 1.915 * sin(g) + 0.020 * sin(2*g)))

    e = radians((23.439 - 0.00000036 * d) % 360)
    RA = degrees(atan2(cos(e) * sin(L), cos(L))) / 15

    declination = degrees(asin(sin(e) * sin(L)))
    equationOfTime = degrees(q)/15 - (RA % 24)
    return declination, equationOfTime


def horizonEquation(angle, latitude, declination):
    """
    The equation that computes the time taken for the sun to reach from the
    highest point in the sky (~thuhr) to a given angle below the horizon.

    In some literature, this equation is also denoted as just 'T'.

    :param angle: Number, the angle the sun should reach below the horizon in degrees.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param declination: Number, the declination of the sun in degrees.
    :return: datetime.timedelta, the time taken for the sun to reach the angle.
    """
    a = radians(angle)
    LAT = radians(latitude)
    DEC = radians(declination)

    h = 1/15 * degrees(acos((-sin(a) - sin(LAT)*sin(DEC)) / (cos(LAT)*cos(DEC))))
    return dt.timedelta(hours=h)


def asrEquation(shadowLength, latitude, declination):
    """
    The equation that computes the time taken for the shadow of an object
    to reach T times its length from when the sun is at its highest point (~thuhr).

    In some literature, this equation is also denoted as just 'A'.

    :param shadowLength: Number, the multiplier for the length of an object's shadow.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param declination: Number, the declination of the sun in degrees.
    :return: datetime.timedelta, the time taken for an object's shadow to reach
    N times its length from when the sun is at its highest point (~thuhr).
    """
    SHA = shadowLength
    LAT = radians(latitude)
    DEC = radians(declination)

    acot = lambda x: atan(1/x)
    h = 1/15 * degrees(acos((sin(acot(SHA + tan(LAT - DEC))) - sin(LAT)*sin(DEC)) / (cos(LAT)*cos(DEC))))
    return dt.timedelta(hours=h)


################################################# NUMERICAL FUNCTIONS

def computeDiff(p1, p2):
    """
    Calculates the difference between two prayers in minutes.

    :param p1: datetime.datetime, the first prayer.
    :param p2: datetime.datetime, the second prayer.
    :return: 3-Tuple, (hours, minutes, seconds)
    """
    if p2 > p1:
        diff = p2 - p1
    else:
        diff = p1 - p2

    hours, remainder = divmod(diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return hours, minutes, seconds

# def __guessKhobarCoordinates():
#     """
#     Attempts to find the coordinates for my hometown in Khobar.
#
#     NOTE: This function is only for personal use and has hardcoded values.
#     """
#     timezone = 3
#     fajrIshaConvention = "umm_alqura"
#     asrConvention = "standard"
#     coord = longitude, latitude = 50.0000, 26.6000
#
#     FORMAT = "%Y-%m-%d %H:%M"
#     date = dt.datetime(2019, 1, 27)
#     fajr = dt.datetime.strptime("2019-01-27 05:03", FORMAT)
#     thuhr = dt.datetime.strptime("2019-01-27 11:53", FORMAT)
#     asr = dt.datetime.strptime("2019-01-27 14:57", FORMAT)
#     maghrib = dt.datetime.strptime("2019-01-27 17:19", FORMAT)
#     isha = dt.datetime.strptime("2019-01-27 18:49", FORMAT)
#     prayers = [fajr, thuhr, asr, maghrib, isha]
#
#     longitudeRange = [longitude-2, longitude+2]
#     latitudeRange = [latitude-2, latitude+2]
#
#     longitude, latitude, err = \
#         guessCoordinates(prayers,
#                          longitudeRange, latitudeRange,
#                          date, timezone, fajrIshaConvention, asrConvention)
#     print("Khobar Coordinates: LON={}, LAT={}, ERR={}".format(longitude, latitude, err))
#
#
# def guessCoordinates(prayers,
#                      longitudeRange, latitudeRange,
#                      date, timezone, fajrIshaConvention, asrConvention,
#                      guesses=10000):
#     """
#     This function brute forces numerically the actual latitude and longitude
#     coordinates for the given prayer times.
#
#     Randomly generates latitude and longitude coordinates within a given
#     range of values, then computes the corresponding prayer times, and then
#     finds the error between these prayer times and the actual prayer times.
#
#     :param prayers: 5-List, [fajr, thuhr, asr, maghrib, isha].
#     :param longitudeRange: 2-List, [startLonGuess, endLonGuess].
#     :param latitudeRange: 2-List, [startLatGuess, endLatGuess].
#     :param date: datetime.datetime, representing the Gregorian date.
#     :param timezone: Number, the timezone of the point of interest in hours.
#     :param fajrIshaConvention: String, the angle convention (see dictionary below).
#     :param asrConvention: String, the shadow length multiplier (see dictionary below).
#     :param guesses: Number, the amount of iterations to try.
#     :return: 3-Tuple, (lowestCumulativeErrorInMinutes, guessLat, guessLon).
#     """
#     points = {}
#
#     for i in range(guesses):
#         longitude = random.uniform(*longitudeRange)
#         latitude = random.uniform(*latitudeRange)
#         coord = (longitude, latitude)
#
#         ps = computePrayerTimes(date, coord, timezone, fajrIshaConvention, asrConvention)
#         ps = [prayer for name, prayer in ps.items()]
#
#         errorFunction = lambda hour, min, sec: 60*hour + min + sec/60
#         err = [errorFunction(*computeDiff(p1, p2)) for p1, p2 in zip(prayers, ps)]
#         err = sum(err)
#         points[err] = (longitude, latitude)
#
#     err, (longitude, latitude) = sorted(points.items(), reverse=True).pop()
#     return longitude, latitude, err
#
#
