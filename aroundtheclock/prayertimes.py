"""
Compute muslim prayer times based on astronomical formulae.
"""

import datetime as dt
from math import acos, asin, atan2, cos, degrees, radians, sin

import julian


def computeFajr(thuhr, angle, latitude, declination, horizonEquation):
    """
    Calculates the time of Fajr prayer.

    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :param angle: Number, the angle convention used to calculated Fajr.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param declination: Number, the declination of the sun in degrees.
    :param horizonEquation: Function, computes time to reach an angle below the horizon.
    :return: datetime.datetime, the datetime of Fajr.
    """
    fajr = thuhr - horizonEquation(angle, latitude, declination)
    return fajr


def computeThuhr(longitude, timeZone, equationOfTime):
    """
    Calculates the time of Thuhr prayer.

    :param longitude: Number, the longitude of the point of interest in degrees.
    :param timeZone: Number, the timezone of the point of interest in degrees.
    :param equationOfTime: Number, mean minus apparent solar time in minutes.
    :return:
    """
    t = 12 + timeZone - (longitude/15 + equationOfTime)
    thuhr = dt.datetime(2019, 2, 4) + dt.timedelta(hours=t)
    return thuhr


def computeJulianDay(year, month, day):
    """
    Converts a Gregorian date to a Julian date.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :return: Number, the corresponding Julian date.
    """
    return julian.to_jd(dt.datetime(year, month, day))


def computeSun(year, month, day):
    """
    Calculates the declination of the sun and the equation of time which are
    needed in prayer calculations.

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

    :param year: Integer, the year to compute the sun parameters.
    :param month: Integer, the month to compute the sun parameters.
    :param day: Integer, the day to compute the sun parameters.
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

    top = -sin(a) - sin(LAT)*sin(DEC)
    bot = cos(LAT)*cos(DEC)
    q = top/bot
    h = 1/15 * degrees(acos(q))
    h = 1/15 * degrees(acos((-sin(a) - sin(LAT)*sin(DEC)) / (cos(LAT)*cos(DEC))))
    return dt.timedelta(hours=h)
