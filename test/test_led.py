import pytest

import setup_paths
setup_paths.setupPaths()
setup_paths.importFakeRPiModule()
import led


def testBlinkLED_TwelveSecondsDuration_sleepCalledForThreeSeconds(mocker):
    mockSleep = mocker.patch("led.time.sleep")
    led.blinkLED(mocker.MagicMock(), 12)

    durationSleep = mockSleep.call_args[0][0]
    timesCalled = mockSleep.call_count
    assert timesCalled * durationSleep == 12

