import datetime as dt
from collections import OrderedDict

import pytest
import schedule
import subprocess
from pytest_mock import mocker

import algorithms
import prayer


######################################## HELPER FUNCTIONS

FORMAT = "%Y-%m-%d %H:%M"


def formatPrayers(prayers):
    """
    Convenience function that re-formats prayer times to a format that is
    easier to use with other functions.

    For example,

    INP: ["2019-01-27", "05:05", "11:53", "14:58", "17:19", "18:49"]
    OUT: ["2019-01-27 05:05",
          "2019-01-27 11:53",
          "2019-01-27 14:58",
          "2019-01-27 17:19",
          "2019-01-27 18:49"]

    :param prayers: 6-List, of the form [date, fajr, thuhr, asr, maghrib, isha].
    :return: 5-List, where each element includes a date and time of the prayer.
    """
    d = prayers[0]
    ps = prayers[1:]
    return ["{} {}".format(d, prayer) for prayer in ps]


def assertAlmostEqualPrayer(p1, p2, err):
    """
    Tests whether the two prayer times are almost equal by checking whether
    they differ by the given amount of minutes.

    :param p1: datetime.datetime, the time of the first prayer.
    :param p2: datetime.datetime, the time of the second prayer.
    :param err: Integer, the number of minutes the prayer can deviate.
    :return: Boolean, true if prayer is in time tolerance otherwise false.
    """
    hours, minutes, seconds = algorithms.computeDiff(p1, p2)
    if abs(60*hours + minutes + seconds/60) > err:
        pytest.fail("Prayer time differs by {:02d}:{:02d}:{:02d}!\np1: {}\np2: {}"
                    .format(hours, minutes, seconds, p1, p2))


class EndOfTestException(Exception):
    """Used in mock objects to halt code execution"""

######################################## TEST DATA (KHOBAR)


mosqueTimings = map(formatPrayers, [
    ["2019-01-27", "05:08", "11:53", "14:58", "17:19", "18:49"],
    ["2019-02-07", "05:00", "11:54", "15:05", "17:28", "18:58"],
    ["2019-02-10", "04:59", "11:54", "15:06", "17:29", "18:59"],
    ["2019-06-02", "03:15", "11:38", "15:05", "18:29", "19:59"],
    ["2019-08-10", "03:42", "11:46", "15:16", "18:21", "19:51"]
])


@pytest.fixture
def kPrayers():
    prayers = OrderedDict({
        "fajr": dt.datetime.strptime("2019-02-04 05:01", FORMAT),
        "thuhr": dt.datetime.strptime("2019-02-04 11:53", FORMAT),
        "asr": dt.datetime.strptime("2019-02-04 15:02", FORMAT),
        "maghrib": dt.datetime.strptime("2019-02-04 17:26", FORMAT),
        "isha": dt.datetime.strptime("2019-02-04 18:29", FORMAT),
    })
    return prayers


@pytest.fixture
def kParams():
    param = {
        "TZ": 3,
        "F_ANG": 18.5,
        "M_ANG": 0.833,
        "I_ANG": 15.0,
        "LON": 50.2083,
        "LAT": 26.2172,
        "SHA": 1,
    }
    return param


######################################## UNIT TESTS


def testFormatPrayers_commonCase_mergeDateWithTime():
    inp = ["2019-01-27", "05:05", "11:53", "14:58", "17:19", "18:49"]
    exp = ["2019-01-27 05:05",
           "2019-01-27 11:53",
           "2019-01-27 14:58",
           "2019-01-27 17:19",
           "2019-01-27 18:49"]
    assert formatPrayers(inp) == exp


def testComputeFajr_khobarCity_calculateKhobarFajr(kPrayers, kParams):
    date = dt.datetime(2019, 2, 4)
    p = prayer.computeFajr(date, kParams["F_ANG"], kParams["LAT"], kPrayers["thuhr"])
    assertAlmostEqualPrayer(p, kPrayers["fajr"], 3)


def testComputeThuhr_khobarCity_calculateKhobarThuhr(kPrayers, kParams):
    date = dt.datetime(2019, 2, 4)
    p = prayer.computeThuhr(date, kParams["LON"], kParams["TZ"])
    assertAlmostEqualPrayer(p, kPrayers["thuhr"], 3)


def testComputeAsr_khobarCity_calculateKhobarAsr(kPrayers, kParams):
    date = dt.datetime(2019, 2, 4)
    p = prayer.computeAsr(date, kParams["SHA"], kParams["LAT"], kPrayers["thuhr"])
    assertAlmostEqualPrayer(p, kPrayers["asr"], 3)


def testComputeMaghrib_khobarCity_calculateKhobarMaghrib(kPrayers, kParams):
    date = dt.datetime(2019, 2, 4)
    p = prayer.computeMaghrib(date, kParams["LAT"], kPrayers["thuhr"], angle=kParams["M_ANG"])
    assertAlmostEqualPrayer(p, kPrayers["maghrib"], 3)


def testComputeIshaUmmAlQura_khobarCity_return90MinuteFromMaghrib():
    isha = dt.datetime.strptime("2019-02-04 18:56", FORMAT)
    maghrib = dt.datetime.strptime("2019-02-04 17:26", FORMAT)
    p = prayer.computeIshaUmmAlQura(maghrib)
    assertAlmostEqualPrayer(p, isha, 0)   # No error acceptable


def testComputeIsha_khobarCity_calculateKhobarIsha(kPrayers, kParams):
    date = dt.datetime(2019, 2, 4)
    p = prayer.computeIsha(date, kParams["I_ANG"], kParams["LAT"], kPrayers["thuhr"])
    assertAlmostEqualPrayer(p, kPrayers["isha"], 3)


@pytest.mark.parametrize("timings", [t for t in mosqueTimings])
def testComputeAllPrayerTimes_khobarCity_calculatePrecisely(timings):
    timings = [dt.datetime.strptime(t, FORMAT) for t in timings]
    date = dt.datetime(timings[0].year, timings[0].month, timings[0].day)
    fajrIshaConvention = "umm_alqura"
    asrConvention = "standard"
    coordinates = (50.0000, 26.6000)
    timezone = 3

    prayers = prayer.computeAllPrayerTimes(date,
                                           coordinates,
                                           timezone,
                                           fajrIshaConvention,
                                           asrConvention)

    for p1, p2 in zip(prayers.values(), timings):
        assertAlmostEqualPrayer(p1, p2, 2)


def testOneTimeJobDecorator_scheduledJob_returnCancelJobWhenDone():
    scheduledFunction = prayer.oneTimeJob(lambda x: 0)
    assert scheduledFunction(0) == schedule.CancelJob


def testBlockInternet_startBlocking_executeOSCommands(mocker):
    mockIPRoute = mocker.Mock(name="ip route")
    mockIPRoute.stdout = b"""
    default via 10.0.2.2 dev enp0s3 proto dhcp metric 100 
    10.0.2.0/24 dev enp0s3 proto kernel scope link src 10.0.2.15 metric 100 
    169.254.0.0/16 dev enp0s3 scope link metric 1000 
    """

    mockSubprocess = mocker.patch("subprocess.run", return_value=mockIPRoute)
    arpPoison = ["sudo", "timeout", "600", "arpspoof", "-i", "enp0s3", "10.0.2.2"]
    kwargs = {"timeout": 600}

    prayer.blockInternet(10)
    mockSubprocess.assert_called_with(arpPoison, **kwargs)


def testBlockInternet_stopBlocking_returnTimeout(mocker):
    calls = [mocker.MagicMock(name="ip route"), subprocess.TimeoutExpired("", 0)]
    mockSubprocess = mocker.patch("subprocess.run", side_effect=calls)

    try:
        prayer.blockInternet(10)
        assert mockSubprocess.call_count == 2
    except subprocess.TimeoutExpired:
        pytest.fail("TimeoutExpired exception was raised when it shouldn't!")


def testWritePrayerTimes_writeToFile_writeCalledProperly(mocker, kPrayers):
    PRAYERS = ["fajr", "thuhr", "asr", "maghrib", "isha"]
    mockOpen = mocker.mock_open()
    _ = mocker.patch("prayer.open", mockOpen)
    mockJSON = mocker.patch("prayer.json")
    unordered = {k: v.strftime("%H:%M") for k, v in kPrayers.items()}
    out = OrderedDict({p: unordered[p] for p in PRAYERS})

    prayer.writePrayerTimes(kPrayers, mocker.MagicMock())
    mockJSON.dump.assert_called_with(out, mockOpen(), **{"indent": 4})


######################################## INTEGRATION TESTS

def testMain_configFileRead_readFileCalled(mocker):
    mockOpen = mocker.mock_open()
    _ = mocker.patch("prayer.open", mockOpen)
    mockJSON = mocker.patch("prayer.json")
    mockJSON.load.side_effect = EndOfTestException

    with pytest.raises(EndOfTestException):
        prayer.main()
    assert mockJSON.load.call_count == 1


def testMain_createOutputDirectory_OSInvoked(mocker):
    mockMkdir = mocker.patch("prayer.Path.mkdir")
    mockMkdir.side_effect = EndOfTestException

    with pytest.raises(EndOfTestException):
        prayer.main()
    assert mockMkdir.call_count == 1


def testMain_scheduleNewPrayerTimes_scheduledAndWaiting(mocker):
    def branchIfElse(*args, **kwargs):
        mockSchedule.default_scheduler.next_run = True

    times = ["05:05", "11:52", "14:56", "17:17", "18:47"]

    _ = mocker.patch("logging.getLogger")
    _ = mocker.patch("sys.stdout")

    mockSchedule = mocker.patch("prayer.schedule")
    mockSchedule.default_scheduler.next_run = False
    mockSchedule.run_pending.side_effect = EndOfTestException
    mockSchedule.every.return_value.day.at.return_value.do.side_effect = branchIfElse

    mockDate = mocker.patch("prayer.dt.date")
    mockDate.today.return_value = dt.datetime(2019, 1, 27)

    with pytest.raises(EndOfTestException):
        prayer.main()
    [mockSchedule.every.return_value.day.at.assert_any_call(t) for t in times]
    assert mockSchedule.every.return_value.day.at.return_value.do.call_count == 5
    assert mockSchedule.run_pending.call_count == 1
