"""
Compute muslim prayer times based on astronomical formulae.

Let T denote a function that computes the time between when the sun is at its
highest point until some angle below the horizon, and let A denote a function
that computes the time from when the sun is at its highest point until the
length of an object's shadow reaches some multiple N. Then, we have the
formulae below.

    Fajr:    T_fajr    = T_thuhr - T(ANGLE)
    Sharooq: T_sharooq = T_thuhr - T(0.833 + hFactor)
    Thuhr:   T_thuhr   = 12 + Tz - (Lng/15 + Te)
    Asr:     T_asr     = T_thuhr + A(MULTIPLIER)
    Maghrib: T_sunset  = T_thuhr + T(0.833 + hFactor)
    Isha:    T_isha    = T_thuhr + T(ANGLE) (or T_maghrib + 90)

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
import json
from collections import OrderedDict

from algorithms import asrEquation, horizonEquation, sunEquation


def writePrayerTimes(prayers, PATH_OUT):
    """
    Writes the prayer times for each prayer into a file in JSON format.

    :param prayers: OrderedDictionary, mapping prayer names to prayer times (datetime objects).
    :param PATH_OUT: Path, the output file to write to.
    """
    DATETIME_FORMAT = "%H:%M"

    prayers = [(p, t.strftime(DATETIME_FORMAT)) for p, t in prayers.items()]
    prayers = OrderedDict(prayers)
    with open(PATH_OUT.as_posix(), 'w+') as f:
        json.dump(prayers, f, indent=4)


def printPrayerTimes(prayers):
    """
    Prints the prayer times in a neat table.

    :param prayers: OrderedDictionary, mapping prayer names to prayer times
    (datetime objects).
    """
    print("Prayer Times:")
    PRINT_FORMAT = "%Y-%m-%d %H:%M"
    for prayer, time in prayers.items():
        print("{:<8}: {}".format(prayer, time.strftime(PRINT_FORMAT)))


def computePrayerTimes(date, coordinates, timezone, fajrIshaConvention, asrConvention):
    """
    Calculates the prayer time for all prayers for a given day.

    :param date: datetime.datetime, representing the Gregorian date.
    :param coordinates: 2-Tuple, (longitude, latitude) of the point of interest in degrees.
    :param timezone: Number, the timezone of the point of interest in hours.
    :param fajrIshaConvention: String, the angle convention (see dictionary below).
    :param asrConvention: String, the shadow length multiplier (see dictionary below).
    :return: OrderedDictionary, mapping prayer names to prayer times (datetime objects).
    """
    PRAYER_NAMES = ["fajr", "thuhr", "asr", "maghrib", "isha"]

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
    LON, LAT = coordinates
    F_ANG, I_ANG = fajrIshaAngle[fajrIshaConvention]
    shadowLength = asrShadow[asrConvention]

    thuhr = computeThuhr(date, LON, TZ)
    fajr = computeFajr(date, F_ANG, LAT, thuhr)
    asr = computeAsr(date, shadowLength, LAT, thuhr)
    maghrib = computeMaghrib(date, LAT, thuhr)

    if I_ANG == "90min":
        isha = computeIshaUmmAlQura(maghrib)
    else:
        isha = computeIsha(date, I_ANG, LAT, thuhr)

    return OrderedDict(zip(PRAYER_NAMES, [fajr, thuhr, asr, maghrib, isha]))


def computeFajr(date, angle, latitude, thuhr):
    """
    Calculates the time of Fajr prayer.

    :param date: datetime.datetime, representing the Gregorian date.
    :param angle: Number, the angle convention used to calculated Fajr.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the datetime of Fajr.
    """
    declination, _ = sunEquation(date)
    fajr = thuhr - horizonEquation(angle, latitude, declination)
    return fajr


def computeThuhr(date, longitude, timeZone):
    """
    Calculates the time of Thuhr prayer.

    :param date: datetime.datetime, representing the Gregorian date.
    :param longitude: Number, the longitude of the point of interest in degrees.
    :param timeZone: Number, the timezone of the point of interest in degrees.
    :return: datetime.datetime, the time of Thuhr prayer.
    """
    _, equationOfTime = sunEquation(date)
    t = 12 + timeZone - (longitude/15 + equationOfTime)
    thuhr = date + dt.timedelta(hours=t)
    return thuhr


def computeAsr(date, shadowLength, latitude, thuhr):
    """
    Calculates the time of Asr prayer.

    :param date: datetime.datetime, representing the Gregorian date.
    :param shadowLength: Number, the multiplier for the length of an object's shadow.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the time of Asr prayer.
    """
    declination, _ = sunEquation(date)
    asr = thuhr + asrEquation(shadowLength, latitude, declination)
    return asr


def computeMaghrib(date, latitude, thuhr, angle=0.833):
    """
    Calculates the time of Maghrib prayer.

    :param date: datetime.datetime, representing the Gregorian date.
    :param angle: Number, the angle convention used to calculated Maghrib.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the datetime of Maghrib.
    """
    declination, _ = sunEquation(date)
    fajr = thuhr + horizonEquation(angle, latitude, declination)
    return fajr


def computeIsha(date, angle, latitude, thuhr):
    """
    Calculates the time of Isha prayer.

    :param date: datetime.datetime, representing the Gregorian date.
    :param angle: Number, the angle convention used to calculated Isha.
    :param latitude: Number, the latitude of the point of interest in degrees.
    :param thuhr: datetime.datetime, Thuhr prayer on the SAME day.
    :return: datetime.datetime, the datetime of Isha.
    """
    declination, _ = sunEquation(date)
    fajr = thuhr + horizonEquation(angle, latitude, declination)
    return fajr


def computeIshaUmmAlQura(maghrib):
    """
    Calculates the time of Isha prayer.

    :param maghrib: datetime.datetime, the time of Maghrib prayer.
    :return: datetime.datetime, the time of Thuhr prayer.
    """
    isha = maghrib + dt.timedelta(minutes=90)
    return isha


def nextFivePrayers(coordinates, timezone, fajrIshaConvention, asrConvention):
    """
    Calculates the five upcoming prayer times based on the current time.

    :param coordinates: 2-Tuple, (longitude, latitude) of the point of interest in degrees.
    :param timezone: Number, the timezone of the point of interest in hours.
    :param fajrIshaConvention: String, the angle convention (see dictionary below).
    :param asrConvention: String, the shadow length multiplier (see dictionary below).
    :return: OrderedDictionary, mapping prayer names to prayer times (datetime objects).
    """
    NOW = dt.datetime.now()
    TODAY = dt.datetime(NOW.year, NOW.month, NOW.day)
    TOMORROW = TODAY + dt.timedelta(days=1)

    prayers = OrderedDict()
    args = [coordinates, timezone, fajrIshaConvention, asrConvention]

    prayersToday = computePrayerTimes(TODAY, *args)
    prayersTomorrow = computePrayerTimes(TOMORROW, *args)

    # Choosing 5 prayers in total: today's remaining prayers + some from tomorrow
    prayersLeftToday = len([t for t in prayersToday.values() if t > NOW])
    [prayersToday.popitem(last=False) for _ in range(5 - prayersLeftToday)]
    [prayersTomorrow.popitem(last=True) for _ in range(prayersLeftToday)]

    prayers.update(prayersToday)
    prayers.update(prayersTomorrow)
    return prayers

