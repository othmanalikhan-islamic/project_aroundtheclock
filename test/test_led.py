import pytest

import setup_paths
setup_paths.setupPaths()
import led


def testMain_configFileRead_readFileCalled(mocker):
    # _ = mocker.patch("led.RPi.GPIO")
    mockSleep = mocker.patch("led.time.sleep")
    led.blinkLED(10, 1)
    assert mockSleep.call_count == 40

