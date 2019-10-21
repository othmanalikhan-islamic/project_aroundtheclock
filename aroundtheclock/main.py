"""
Main entry module for running the project.
"""

import datetime as dt
import json
import logging
import logging.config
import time
from pathlib import Path

import schedule

import led
from block import blockInternet
from prayer import nextFivePrayers, printPrayerTimes, writePrayerTimes

PATH_ROOT = Path(__file__, "../../").absolute().resolve()


def main():
    """
    Runs the script.
    """
    # Reading config file
    PATH_CONFIG = Path(PATH_ROOT, "config/config.json").absolute().resolve()
    with open(PATH_CONFIG.as_posix(), "r") as f:
        CONFIG = json.load(f)
        CONFIG["longitude"] = float(CONFIG["longitude"])
        CONFIG["latitude"] = float(CONFIG["latitude"])
        CONFIG["timezone"] = int(CONFIG["timezone"])

    # Creating output directory
    PATH_OUT = Path(CONFIG["path"]["output"])
    PATH_OUT.mkdir(parents=True, exist_ok=True)

    # Initialising logging
    logging.config.fileConfig(fname=CONFIG["path"]["logging"], disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Starting project AroundTheClock!")

    # Initialising LED
    pin = led.initialisePi(CONFIG["pin"])

    ######################################## SCHEDULING

    # Schedule blocking times for prayers otherwise wait on existing jobs.
    while True:
        if schedule.default_scheduler.next_run:
            blinkSpeed = schedule.default_scheduler.next_run - dt.datetime.now()
            blinkSpeed = blinkSpeed.total_seconds() / 3600
            if blinkSpeed < 0.5:
                blinkSpeed = 0.5
            led.blinkLED(pin, blinkSpeed)
            schedule.run_pending()
        else:
            FORMAT_SCHEDULE = "%H:%M"
            FORMAT_PRINT = "%Y-%m-%d %H:%M"

            # Computing prayer times
            logger.info("Computing next five prayers after {}!".format(dt.date.today()))
            prayers = nextFivePrayers((CONFIG["longitude"], CONFIG["latitude"]),
                                      CONFIG["timezone"],
                                      CONFIG["fajr_isha"],
                                      CONFIG["asr"])

            # Logging prayer times computed
            ps = ["{}: {}".format(p, t.strftime(FORMAT_PRINT)) for p, t in prayers.items()]
            timings = ", ".join(ps)
            logger.info("Prayer times generated: {}.".format(timings))
            writePrayerTimes(prayers, Path(CONFIG["path"]["prayer"]))
            printPrayerTimes(prayers)

            # Scheduling prayer block times as jobs
            for p, t in prayers.items():
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
