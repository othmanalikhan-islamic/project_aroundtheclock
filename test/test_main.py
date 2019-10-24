import datetime as dt
import json
from pathlib import Path

import pytest

import setup_paths
setup_paths.setupPaths()
setup_paths.importFakeRPiModule()
import main as main

######################################## HELPER FUNCTIONS


class EndOfTestException(Exception):
    """Used in mock objects to halt code execution"""


class MockToday(dt.datetime):
    @classmethod
    def now(cls):
        return cls(2019, 1, 27)


class MockBeforeMaghrib(dt.datetime):
    @classmethod
    def now(cls):
        return cls(2019, 1, 27, 17, 16, 0)


######################################## INTEGRATION TESTS


@pytest.fixture(scope="session", autouse=True)
def createOutputDirectory():
    PATH_ROOT = Path(__file__, "../../").absolute().resolve()

    # Reading config file
    PATH_CONFIG = Path(PATH_ROOT, "config/config.json").absolute().resolve()
    with open(PATH_CONFIG.as_posix(), "r") as f:
        CONFIG = json.load(f)

    # Creating output directory
    PATH_OUT = Path(CONFIG["path"]["output"])
    PATH_OUT.mkdir(parents=True, exist_ok=True)


def testMain_configFileRead_readFileCalled(mocker):
    mockOpen = mocker.mock_open()
    _ = mocker.patch("main.open", mockOpen)
    mockJSON = mocker.patch("main.json")
    mockJSON.load.side_effect = EndOfTestException

    with pytest.raises(EndOfTestException):
        main.main()
    assert mockJSON.load.call_count == 1


def testMain_createOutputDirectory_OSInvoked(mocker):
    mockMkdir = mocker.patch("main.Path.mkdir")
    mockMkdir.side_effect = EndOfTestException

    with pytest.raises(EndOfTestException):
        main.main()
    assert mockMkdir.call_count == 1


def testMain_scheduleNewPrayerTimes_scheduleAndWait(mocker):
    def branchIfElse(*args, **kwargs):
        mockSchedule.default_scheduler.next_run = dt.datetime(2019, 1, 27, 12)

    times = ["05:05", "11:52", "14:56", "17:17", "18:47"]

    _ = mocker.patch("sys.stdout")
    _ = mocker.patch("logging.getLogger")
    _ = mocker.patch("main.json.dump")
    _ = mocker.patch("main.Path.mkdir")
    mockLED = mocker.patch("main.led")

    mockSchedule = mocker.patch("main.schedule")
    mockSchedule.default_scheduler.next_run = None
    mockSchedule.run_pending.side_effect = EndOfTestException
    mockSchedule.every.return_value.day.at.return_value.do.side_effect = branchIfElse

    main.dt.datetime = MockToday

    # Catching exception as a means to break infinite while loop in source code
    with pytest.raises(EndOfTestException):
        main.main()

    # Check if block times have been scheduled
    [mockSchedule.every.return_value.day.at.assert_any_call(t) for t in times]
    assert mockSchedule.every.return_value.day.at.return_value.do.call_count == 5

    # Check if LED blinked
    assert mockLED.blinkLED.call_count == 1

    # Check if scheduled jobs attempted to be executed
    assert mockSchedule.run_pending.call_count == 1

