"""
Block internet connectivity via arp poisoning.
"""

import functools
import logging
import logging.config
import shlex
import subprocess

import schedule


def oneTimeJob(func):
    """
    Decorator that causes the given scheduled function to run only once.
    As a bonus, it also logs the subsequent job to be ran.

    NOTE: This decorator suppresses any returned results by the given function.

    :param func: function, the function to be wrapped.
    :return: function, the wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)   # Outside try-except to allow exception bubbling
        try:
            logging.info("Next job at {}.".format(schedule.jobs[1].next_run))
        except IndexError:
            logging.info("No next job scheduled!")
        finally:
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
    try:
        # Send output to PIPE to store in buffer
        cmdRoute = "ip route"
        p1 = subprocess.run(shlex.split(cmdRoute), stdout=subprocess.PIPE)
        GATEWAY = p1.stdout.split()[2].decode("ascii")
        INTERFACE = p1.stdout.split()[4].decode("ascii")
        logging.info("Found GW={}, INT={}".format(GATEWAY, INTERFACE))
    except IndexError:
        logging.exception("The output of 'ip route' is empty! It looks like"
                          "The OS networking service might need a restart!")
        raise OSError("'ip route' failed to return output!")

    # Arp spoof entire network for a limited duration
    logging.info("Blocking internet for {} minute(s)!".format(duration))
    seconds = int(duration * 60)
    cmdBlock = "sudo aroundtheclock {} {} {}".format(INTERFACE, GATEWAY, seconds)
    logging.info("Ran the following command to block: '{}'".format(cmdBlock))
    subprocess.run(shlex.split(cmdBlock))
    logging.info("Block time over, unblocking internet now!")
