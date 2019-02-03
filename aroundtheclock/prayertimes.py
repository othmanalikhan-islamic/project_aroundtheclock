"""
Compute muslim prayer times based on astronomical formulae.
"""

from datetime import datetime as dt
from math import acos, asin, atan2, cos, radians, sin

import julian


def computeJulianDay(year, month, day):
    """
    Converts a Gregorian date to a Julian date.

    :param year: Integer, the year.
    :param month: Integer, the month.
    :param day: Integer, the day.
    :return: Float, the corresponding julian date.
    """
    return julian.to_jd(dt(year, month, day))


# Julian Day (Virtual Reality and Augmented Reality: 15th EuroVR International Conference)
def Julian(year, month, day):
    d = (367 * year) - ((year + (int)((month + 9) / 12)) * 7 / 4) + (((int)(275 * month / 9)) + day - 730531.5);

    g = radians(357.529 + 0.98560028* d);
    q = radians(280.459 + 0.98564736* d);
    L = radians(q + 1.915* sin(g) + 0.020* sin(2*g))

    R = 1.00014 - 0.01671* cos(g) - 0.00014* cos(2*g)
    e = radians(23.439 - 0.00000036* d)
    RA = atan2(cos(e)* sin(L), cos(L))/ 15

    D = asin(sin(e)* sin(L))
    EqT = q/15 - RA
    return D, EqT

def T(angle, LAT, DEC):
    return 1/15 * acos((-sin(angle) - sin(LAT)*sin(DEC)) / cos(LAT)*cos(DEC))


def computeFajr(thuhr, angle, LAT, DEC, T):
    """
    :param thuhr: datetime, the time for thuhr.
    :param angle:
    :return: datetime, the time for fajr.
    """
    print(T(angle, LAT, DEC))
    fajr = thuhr - T(angle, LAT, DEC)
    return fajr
