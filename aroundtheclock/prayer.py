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
import functools
import json
import logging
import os
import random
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path

import julian
import schedule
from math import acos, asin, atan, atan2, cos, degrees, radians, sin, tan

PATH_ROOT = Path(__file__, "../../")

################################################# DECORATORS


def oneTimeJob(func):
    """
    Decorator that causes the given scheduled function to run only once.
    As a bonus, it also logs the subsequent job to be ran.

    NOTE: This decorator suppresses any results returned by the given function.

    :param func: function, the function to be wrapped.
    :return: function, the wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

        # Log when next job is occurring
        try:
            schedule.cancel_job(schedule.jobs[0])
            logging.info("Next job at {}.".format(schedule.default_scheduler.run))
        except Exception:
            pass    # Try or die trying...

        return schedule.CancelJob
    return wrapper


################################################# PUBLIC FUNCTIONS (SCHEDULING)


@oneTimeJob
def blockInternet(duration):
    """
    For the physical device running this script that is connected to a
    network, arp poisons its default gateway on the network for all hosts,
    thereby 'suspending' connectivity to WAN (internet) for the given duration.

    Pre-requisites for this function to run properly:
        1. Install arpspoof on OS: sudo apt-get install dsniffer.
        2. Run this function using an OS account with privileges.

    :param duration: Integer, the block duration in minutes.
    :return: Scheduler.CancelJob, making this function a one-off job (no repeat).
    """
    # Fetch network parameters from OS for arp spoofing
    p1 = subprocess.run(["ip", "route"], stdout=subprocess.PIPE)
    GATEWAY = p1.stdout.split()[2].decode("ascii")
    INTERFACE = p1.stdout.split()[4].decode("ascii")
    logging.info("Found GW={}, INT={}".format(GATEWAY, INTERFACE))

    # Arp spoof entire network for a limited duration
    try:
        logging.info("Blocking internet for {} minute(s)!".format(duration))
        seconds = duration*60
        subprocess.run(["sudo", "timeout", str(seconds), "arpspoof", "-i", INTERFACE, GATEWAY],
                       timeout=seconds)
    except subprocess.TimeoutExpired:
        logging.info("Block time over, unblocking internet now!")


################################################# PUBLIC FUNCTIONS (PRAYER)


def writePrayerTimes(prayers, PATH_OUT):
    """
    Writes the prayer times for each prayer into a file in JSON format.

    :param prayers: OrderedDictionary, mapping prayer names to prayer times (datetime objects).
    :param PATH_OUT: Path, the output file to write to.
    """
    DATETIME_FORMAT = "%H:%M"

    prayers = [(p, t.strftime(DATETIME_FORMAT)) for p, t in prayers.items()]
    prayers = OrderedDict(prayers)
    with open(str(PATH_OUT), 'w') as f:
        json.dump(prayers, f, indent=4)


def printAllPrayerTimes(prayers):
    """
    Prints the prayer times in a neat table.

    :param prayers: OrderedDictionary, mapping prayer names to prayer times
    (datetime objects).
    """
    print("Prayer Times:")
    PRINT_FORMAT = "%Y-%m-%d %H:%M"
    for prayer, time in prayers.items():
        print("{:<8}: {}".format(prayer, time.strftime(PRINT_FORMAT)))


def computeAllPrayerTimes(date, coordinates, timezone, fajrIshaConvention, asrConvention):
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
        isha = computeIsha(date,  I_ANG, LAT, thuhr)

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
    declination, _ = _sunEquation(date)
    fajr = thuhr - _horizonEquation(angle, latitude, declination)
    return fajr


def computeThuhr(date, longitude, timeZone):
    """
    Calculates the time of Thuhr prayer.

    :param date: datetime.datetime, representing the Gregorian date.
    :param longitude: Number, the longitude of the point of interest in degrees.
    :param timeZone: Number, the timezone of the point of interest in degrees.
    :return: datetime.datetime, the time of Thuhr prayer.
    """
    _, equationOfTime = _sunEquation(date)
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
    declination, _ = _sunEquation(date)
    asr = thuhr + _asrEquation(shadowLength, latitude, declination)
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
    declination, _ = _sunEquation(date)
    fajr = thuhr + _horizonEquation(angle, latitude, declination)
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
    declination, _ = _sunEquation(date)
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


################################################# PRIVATE FUNCTIONS


def _julianEquation(date):
    """
    Converts a Gregorian date to a Julian date.

    :param date: datetime.datetime, representing the Gregorian date.
    :return: Number, the corresponding Julian date.
    """
    return julian.to_jd(date)


def _sunEquation(date):
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
    d = _julianEquation(date) - 2451545.0

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


################################################# NUMERICAL FUNCTIONS


def __guessKhobarCoordinates():
    """
    Attempts to find the coordinates for my hometown in Khobar.

    NOTE: This function is only for personal use and has hardcoded values.
    """
    timezone = 3
    fajrIshaConvention = "umm_alqura"
    asrConvention = "standard"
    coord = longitude, latitude = 50.0000, 26.6000

    FORMAT = "%Y-%m-%d %H:%M"
    date = dt.datetime(2019, 1, 27)
    fajr = dt.datetime.strptime("2019-01-27 05:03", FORMAT)
    thuhr = dt.datetime.strptime("2019-01-27 11:53", FORMAT)
    asr = dt.datetime.strptime("2019-01-27 14:57", FORMAT)
    maghrib = dt.datetime.strptime("2019-01-27 17:19", FORMAT)
    isha = dt.datetime.strptime("2019-01-27 18:49", FORMAT)
    prayers = [fajr, thuhr, asr, maghrib, isha]

    longitudeRange = [longitude-2, longitude+2]
    latitudeRange = [latitude-2, latitude+2]

    longitude, latitude, err = \
        guessCoordinates(prayers,
                         longitudeRange, latitudeRange,
                         date, timezone, fajrIshaConvention, asrConvention)
    print("Khobar Coordinates: LON={}, LAT={}, ERR={}".format(longitude, latitude, err))


def guessCoordinates(prayers,
                     longitudeRange, latitudeRange,
                     date, timezone, fajrIshaConvention, asrConvention,
                     guesses=10000):
    """
    This function brute forces numerically the actual latitude and longitude
    coordinates for the given prayer times.

    Randomly generates latitude and longitude coordinates within a given
    range of values, then computes the corresponding prayer times, and then
    finds the error between these prayer times and the actual prayer times.

    :param prayers: 5-List, [fajr, thuhr, asr, maghrib, isha].
    :param longitudeRange: 2-List, [startLonGuess, endLonGuess].
    :param latitudeRange: 2-List, [startLatGuess, endLatGuess].
    :param date: datetime.datetime, representing the Gregorian date.
    :param timezone: Number, the timezone of the point of interest in hours.
    :param fajrIshaConvention: String, the angle convention (see dictionary below).
    :param asrConvention: String, the shadow length multiplier (see dictionary below).
    :param guesses: Number, the amount of iterations to try.
    :return: 3-Tuple, (lowestCumulativeErrorInMinutes, guessLat, guessLon).
    """
    points = {}

    for i in range(guesses):
        longitude = random.uniform(*longitudeRange)
        latitude = random.uniform(*latitudeRange)
        coord = (longitude, latitude)

        ps = computeAllPrayerTimes(date, coord, timezone, fajrIshaConvention, asrConvention)
        ps = [prayer for name, prayer in ps.items()]

        errorFunction = lambda hour, min, sec: 60*hour + min + sec/60
        err = [errorFunction(*computeDiff(p1, p2)) for p1, p2 in zip(prayers, ps)]
        err = sum(err)
        points[err] = (longitude, latitude)

    err, (longitude, latitude) = sorted(points.items(), reverse=True).pop()
    return longitude, latitude, err


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


################################################# RUNNING SCRIPT


def main(CONFIG):
    """
    Runs the script.

    :param CONFIG: Dictionary, containing JSON data of config.json.
    """
    ######################################## INITIALISING VARIABLES

    longitude, latitude = float(CONFIG["longitude"]), float(CONFIG["latitude"])
    coord = (longitude, latitude)
    timezone = int(CONFIG["timezone"])
    fajrIshaConv = CONFIG["fajr_isha"]
    asrConv = CONFIG["asr"]
    PATH_JSON = Path(CONFIG["path"]["prayer"])
    blockMapping = CONFIG["block"]

    ######################################## SCHEDULING

    # Schedule today's prayer blocking times otherwise wait on existing jobs.
    while True:
        if schedule.default_scheduler.next_run:
            schedule.run_pending()
            time.sleep(1)
        else:
            FORMAT_SCHEDULE = "%H:%M"
            FORMAT_PRINT = "%Y-%m-%d %H:%M"

            # Computing prayer times
            logging.info("Computing today's prayer times {}!".format(dt.date.today()))
            t = dt.date.today()
            date = dt.datetime(t.year, t.month, t.day)
            prayers = computeAllPrayerTimes(date, coord, timezone, fajrIshaConv, asrConv)

            # Logging prayer times computed
            ps = ["{}: {}".format(p, t.strftime(FORMAT_PRINT)) for p, t in prayers.items()]
            timings = ", ".join(ps)
            logging.info("Prayer times generated: {}.".format(timings))
            writePrayerTimes(prayers, PATH_JSON)
            printAllPrayerTimes(prayers)

            # Scheduling prayer block times as jobs
            # NOTE: This logic is simple and sometimes allows prayers from
            # yesterday to be scheduled for tomorrow. Undesirable but not
            # much of an issue as delta between prayers 1 day apart is no
            # more than 2 minutes.
            for p, t in prayers.items():
                t = t.strftime(FORMAT_SCHEDULE)
                duration = blockMapping[p]
                schedule.every().day.at(t).do(blockInternet, duration)

            # Logging scheduled jobs
            for j in schedule.jobs:
                logging.info("Job scheduled: {}.".format(j))
            logging.info("Next job at {}.".format(schedule.default_scheduler.next_run))


if __name__ == "__main__":
    try:
        # Reading config file
        PATH_CONFIG = Path(PATH_ROOT, "config.json")
        with open(str(PATH_CONFIG), "r") as f:
            CONFIG = json.load(f)

        # Creating output directory
        PATH_OUT = Path(PATH_ROOT, "output")
        PATH_OUT.mkdir(parents=True, exist_ok=True)

        # Initialising logging

        FORMAT_LOG = "%(asctime)s: %(message)s"
        FORMAT_TIME = "%Y-%m-%d %H:%M:%S"
        fileHandler = logging.FileHandler(CONFIG["path"]["log"])
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(logging.Formatter(FORMAT_LOG, FORMAT_TIME))
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(FORMAT_LOG, FORMAT_TIME))

        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(console)
        root.addHandler(fileHandler)

        main(CONFIG)

    except Exception as e:
        logging.exception("An unexpected error has occured!")
