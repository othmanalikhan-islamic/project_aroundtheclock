"""
Block internet connectivity via arp poisoning.
"""

import functools
import logging
import logging.config
import shlex
import subprocess
from subprocess import PIPE, Popen
from threading import Timer

import schedule


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
        try:
            logging.info("Next job at {}.".format(schedule.jobs[1].next_run))
        except IndexError:
            logging.info("No next job scheduled!")
        finally:
            func(*args, **kwargs)
            return schedule.CancelJob
    return wrapper


@oneTimeJob
def blockInternet(duration):
    """
    For the physical device running this script that is connected to a
    network, arp poisons its default gateway on the network for all hosts,
    thereby 'suspending' connectivity to WAN (internet) for the given duration.

    Pre-requisites for this function to run properly:
        1. Install arpspoof on OS: sudo apt-get install dsniff.
        2. Run this function using an OS account with root privileges.

    :param duration: Integer, the block duration in minutes.
    :return: Scheduler.CancelJob, making this function a one-off job (no repeat).
    """
    # Fetch network parameters from OS for arp spoofing
    p1 = subprocess.run(["ip", "route"], stdout=subprocess.PIPE)
    GATEWAY = p1.stdout.split()[2].decode("ascii")
    INTERFACE = p1.stdout.split()[4].decode("ascii")
    logging.info("Found GW={}, INT={}".format(GATEWAY, INTERFACE))

    # Arp spoof entire network for a limited duration
    seconds = duration * 60
    cmd = "sudo arpspoof -i {} {}".format(INTERFACE, GATEWAY)
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    timer = Timer(seconds, proc.kill)
    logging.info("Blocking internet for {} minute(s)!".format(duration))
    logging.info("Ran the following command to block: '{}'".format(cmd))

    try:
        timer.start()
    finally:
        logging.info("Block time over, unblocking internet now!")
        timer.cancel()
