"""
Compute muslim prayer times based on astronomical formulae.

Let T denote a function that computes the time between when the sun is at its
highest point until some angle below the horizon, and let A denote a function
that computes the time from when the sun is at its highest point until the
length of an object's shadow reaches some multiple N. Then, we have the
formulae below.

    Fajr:    T_fajr    = T_dhuhr - T(ANGLE)
    Sharooq: T_sharooq = T_dhuhr - T(0.833 + hFactor)
    Dhuhr:   T_dhuhr   = 12 + Tz - (Lng/15 + Te)
    Asr:     T_asr     = T_dhuhr + A(MULTIPLIER)
    Maghrib: T_sunset  = T_dhuhr + T(0.833 + hFactor)
    Isha:    T_isha    = T_dhuhr + T(ANGLE) (or T_maghrib + 90)

    where
        hFactor = 0.0347 * h^0.5, the height factor
        ANGLE = angle convention for a particular prayer
        Tz = Timezone
        Lng = Longitude

Note, that some additional parameters are needed for functions T and A however
in the formulae above they are omitted for simplicity. See the code
implementation for more details.
"""

import datetime as dt
import random
from math import acos, asin, atan, atan2, cos, degrees, radians, sin, tan
from pprint import pprint

import julian


def computeAllPrayerTimes(year, month, day,
                          longitude, latitude,
                          timezone,
                          fajrIshaConvention,
                          asrConvention):
    """
    Calculates the prayer time for all prayers for a given day.

    :param year: Integer, the year to compute the sun parameters.
    :param month: Integer, the month to compute the sun parameters.
    :param day: Integer, the day to compute the sun parameters.
    :param longitude: Number, the longitude of the point of interest in degrees.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param timezone: Number, the timezone of the point of interest in hours.
    :param fajrIshaConvention: String, the angle convention (see dictionary below).
    :param asrConvention: String, the shadow length multiplier (see dictionary below).
    :return: 5-List, [fajr, thuhr, asr, maghrib, isha] as datetime objects.
    """
    fajrIshaAngle = {
        "muslim_league": (18, 17),
        "isna": (15, 15),
        "egypt": (19.5, 17.5),
        "umm_alqura": (18.5, "90min")
    }

    asrShadow = {
        "standard": 1,
        "hanafi": 2
    }

    TZ = timezone
    LON = longitude
    LAT = latitude
    F_ANG, I_ANG = fajrIshaAngle[fajrIshaConvention]
    shadowLength = asrShadow[asrConvention]

    thuhr = computeThuhr(year, month, day, LON, TZ)
    fajr = computeFajr(year, month, day, F_ANG, LAT, thuhr)
    asr = computeAsr(year, month, day, shadowLength, LAT, thuhr)
    maghrib = computeMaghrib(year, month, day, LAT, thuhr)

    if I_ANG == "90min":
        isha = computeIshaUmmAlQura(maghrib)
    else:
        isha = computeIsha(year, month, day, I_ANG, LAT, thuhr)

    return [fajr, thuhr, asr, maghrib, isha]


def computeFajr(year, month, day, angle, latitude, thuhr):
    """
    Calculates the time of Fajr prayer.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :param angle: Number, the angle convention used to calculated Fajr.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the datetime of Fajr.
    """
    declination, _ = _sunEquation(year, month, day)
    fajr = thuhr - _horizonEquation(angle, latitude, declination)
    return fajr


def computeThuhr(year, month, day, longitude, timeZone):
    """
    Calculates the time of Thuhr prayer.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :param longitude: Number, the longitude of the point of interest in degrees.
    :param timeZone: Number, the timezone of the point of interest in degrees.
    :return: datetime.datetime, the time of Thuhr prayer.
    """
    _, equationOfTime = _sunEquation(year, month, day)
    t = 12 + timeZone - (longitude/15 + equationOfTime)
    thuhr = dt.datetime(year, month, day) + dt.timedelta(hours=t)
    return thuhr


def computeAsr(year, month, day, shadowLength, latitude, thuhr):
    """
    Calculates the time of Asr prayer.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :param shadowLength: Number, the multiplier for the length of an object's shadow.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the time of Asr prayer.
    """
    declination, _ = _sunEquation(year, month, day)
    asr = thuhr + _asrEquation(shadowLength, latitude, declination)
    return asr


def computeMaghrib(year, month, day, latitude, thuhr, angle=0.833):
    """
    Calculates the time of Maghrib prayer.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :param angle: Number, the angle convention used to calculated Maghrib.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the datetime of Maghrib.
    """
    declination, _ = _sunEquation(year, month, day)
    fajr = thuhr + _horizonEquation(angle, latitude, declination)
    return fajr


def computeIsha(year, month, day, angle, latitude, thuhr):
    """
    Calculates the time of Isha prayer.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :param angle: Number, the angle convention used to calculated Isha.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the datetime of Isha.
    """
    declination, _ = _sunEquation(year, month, day)
    fajr = thuhr + _horizonEquation(angle, latitude, declination)
    return fajr


def computeIshaUmmAlQura(maghrib):
    """
    Calculates the time of Isha prayer.

    :param maghrib: datetime.datetime, the time of Maghrib prayer.
    :return: datetime.datetime, the time of Thuhr prayer.
    """
    isha = maghrib + dt.timedelta(minutes=90)
    return isha


def _julianEquation(year, month, day):
    """
    Converts a Gregorian date to a Julian date.

    :param year: Integer, the Gregorian year.
    :param month: Integer, the Gregorian month.
    :param day: Integer, the Gregorian day.
    :return: Number, the corresponding Julian date.
    """
    return julian.to_jd(dt.datetime(year, month, day))


def _sunEquation(year, month, day):
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
    d = _julianEquation(year, month, day) - 2451545.0

    g = radians((357.529 + 0.98560028 * d) % 360)
    q = radians((280.459 + 0.98564736 * d) % 360)
    L = radians((degrees(q) + 1.915 * sin(g) + 0.020 * sin(2*g)))

    e = radians((23.439 - 0.00000036 * d) % 360)
    RA = degrees(atan2(cos(e) * sin(L), cos(L))) / 15

    declination = degrees(asin(sin(e) * sin(L)))
    equationOfTime = degrees(q)/15 - (RA % 24)
    return declination, equationOfTime


def _horizonEquation(angle, latitude, declination):
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


def _asrEquation(shadowLength, latitude, declination):
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


def computeError(prayers, latitudeRange, longitudeRange):
    """
    This function brute forces numerically the actual latitude and longitude
    coordinates for the given prayer times.

    Randomly generates latitude and longitude coordinates within a given
    range of values, then computes the corresponding prayer times, and then
    finds the error between these prayer times and the actual prayer times.

    :param prayers: 5-List, [fajr, thuhr, asr, maghrib, isha].
    :param latitudeRange: 2-List, [startLatGuess, endLatGuess].
    :param longitudeRange: 2-List, [startLonGuess, endLonGuess].
    :return: 3-Tuple, (lowestCumulativeErrorInMinutes, guessLat, guessLon).
    """
    pass


def computeError(p1, p2):
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


def main():
    t = dt.datetime.today()
    year, month, day = t.year, t.month, t.day
    year, month, day = 2019, 1, 27
    longitude, latitude = 49.8000, 26.5172
    timezone = 3
    fajrIshaConvention = "umm_alqura"
    asrConvention = "standard"


    FORMAT = "%Y-%m-%d %H:%M"
    fajr = dt.datetime.strptime("2019-01-27 05:03", FORMAT)
    thuhr = dt.datetime.strptime("2019-01-27 11:53", FORMAT)
    asr = dt.datetime.strptime("2019-01-27 14:57", FORMAT)
    maghrib = dt.datetime.strptime("2019-01-27 17:19", FORMAT)
    isha = dt.datetime.strptime("2019-01-27 18:49", FORMAT)
    prayers = [fajr, thuhr, asr, maghrib, isha]



    points = {}

    for i in range(10000):
        longitude = random.uniform(49, 51)
        latitude = random.uniform(25, 27)

        ps = computeAllPrayerTimes(year, month, day,
                                        longitude, latitude,
                                        timezone,
                                        fajrIshaConvention,
                                        asrConvention)

        err = 0
        for i in range(5):
            hours, minutes, seconds = computeError(prayers[i], ps[i])
            err += 60*hours + minutes + seconds/60

        points[err] = (longitude, latitude)

    for p, (lon, lat) in sorted(points.items()):
        print("({}, {}) -> {}".format(lon, lat, p))

    pprint(prayers)


if __name__ == "__main__":
    main()
