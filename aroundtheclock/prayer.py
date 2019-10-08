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
import functools
import json
import logging
import subprocess
import time
import logging.config
from collections import OrderedDict
from pathlib import Path
from algorithms import sunEquation, horizonEquation, asrEquation

import schedule

PATH_ROOT = Path(__file__, "../../").absolute().resolve()

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
        logging.info("Next job at {}.".format(schedule.default_scheduler.next_run))
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
    with open(PATH_OUT.as_posix(), 'w') as f:
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


################################################# RUNNING SCRIPT


def main():
    """
    Runs the script.
    """
    # Reading config file
    PATH_CONFIG = Path(PATH_ROOT, "config/config.json").absolute().resolve()
    with open(PATH_CONFIG.as_posix(), "r") as f:
        CONFIG = json.load(f)

    # Creating output directory
    PATH_OUT = Path(CONFIG["path"]["output"])
    PATH_OUT.mkdir(parents=True, exist_ok=True)

    # Initialising logging
    logging.config.fileConfig(fname=CONFIG["path"]["logging"], disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Starting project AroundTheClock!")

    ######################################## SCHEDULING

    # Schedule today's prayer blocking times otherwise wait on existing jobs.
    while True:
        if schedule.default_scheduler.next_run:
            schedule.run_pending()
            time.sleep(1)
        else:
            FORMAT_SCHEDULE = "%H:%M"
            FORMAT_PRINT = "%Y-%m-%d %H:%M"
            NOW = dt.datetime.now()
            TODAY = dt.datetime(NOW.year, NOW.month, NOW.day)

            # Computing prayer times
            logger.info("Computing today's prayer times {}!".format(dt.date.today()))
            prayers = computeAllPrayerTimes(TODAY,
                                            (float(CONFIG["longitude"]),
                                             float(CONFIG["latitude"])),
                                            int(CONFIG["timezone"]),
                                            CONFIG["fajr_isha"],
                                            CONFIG["asr"])

            # Logging prayer times computed
            ps = ["{}: {}".format(p, t.strftime(FORMAT_PRINT)) for p, t in prayers.items()]
            timings = ", ".join(ps)
            logger.info("Prayer times generated: {}.".format(timings))
            writePrayerTimes(prayers, Path(CONFIG["path"]["prayer"]))
            printAllPrayerTimes(prayers)

            # Scheduling prayer block times as jobs
            for p, t in prayers.items():
                # if t > NOW:
                    t = t.strftime(FORMAT_SCHEDULE)
                    duration = CONFIG["block"][p]
                    schedule.every().day.at(t).do(blockInternet, duration)

            # Logging scheduled jobs
            for j in schedule.jobs:
                logger.info("Job scheduled: {}.".format(j))
            logger.info("Next job at {}.".format(schedule.default_scheduler.next_run))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("An unexpected error has occurred!")
