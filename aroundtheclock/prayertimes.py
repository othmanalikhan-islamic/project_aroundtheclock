"""
Compute muslim prayer times based on astronomical formulae.
"""

import datetime as dt
from math import acos, asin, atan2, cos, degrees, radians, sin

import julian


def computeFajr(thuhr, angle, LAT, DEC, T):
    """
    :param thuhr: datetime, the time for thuhr.
    :param angle:
    :return: datetime, the time for fajr.
    """
    print(T(angle, LAT, DEC))
    # return dt(2019, 1, 1)

    t = T(angle, LAT, DEC)
    hours, minutes = divmod(t*60, 60)
    print(hours, minutes)
    fajr = thuhr - dt(2019, 1, 1, int(hours), int(minutes))
    return fajr


def computeJulianDay(year, month, day):
    """
    Converts a Gregorian date to a Julian date.

    :param year: Integer, the year.
    :param month: Integer, the month.
    :param day: Integer, the day.
    :return: Number, the corresponding julian date.
    """
    return julian.to_jd(dt.datetime(year, month, day))


def computeSun(year, month, day):
    """
    Calculates the declination of the sun and the equation of time which are
    needed in prayer calculations.

    Equations:
        Equation of Time = Apparent Solar Time - Mean Solar Time
        Declination = The angle between the sun's rays and Earth's equator.

    Abbreviations:
        d - Number of days and fraction from 2000 January 1.5 (J2000.0)
        g - Mean anomaly of the sun
        q - Mean longitude of the sun
        L - Geocentric apparent ecliptic longitude of the sun (adjusted for aberration)
        e - Mean obliquity of the ecliptic
        RA - Right ascension

    :param year: Integer, the year.
    :param month: Integer, the month.
    :param day: Integer, the day.
    :return: 2-Tuple, (declination, equation of time)
    """
    d = computeJulianDay(year, month, day) - 2451545.0

    g = radians((357.529 + 0.98560028 * d) % 360)
    q = radians((280.459 + 0.98564736 * d) % 360)
    L = radians((degrees(q) + 1.915 * sin(g) + 0.020 * sin(2*g)))

    e = radians((23.439 - 0.00000036 * d) % 360)
    RA = degrees(atan2(cos(e) * sin(L), cos(L))) / 15

    declination = degrees(asin(sin(e) * sin(L)))
    equationOfTime = degrees(q)/15 - (RA % 24)
    return declination, equationOfTime


def T(angle, latitude, declination):
    """
    The equation that computes the time taken for the sun to reach a given
    angle below the horizon.

    :param angle: Number, the angle in degrees.
    :param latitude: Number, the latitude in degrees.
    :param declination: Number, the latitude in degrees.
    :return: datetime.timedelta, the time taken for the sun to reach the angle.
    """
    a = radians(angle)
    LAT = radians(latitude)
    DEC = radians(declination)
    t = 1/15 * degrees(acos((-sin(a) - sin(LAT)*sin(DEC)) / (cos(LAT)*cos(DEC))))
    return dt.timedelta(hours=t)
