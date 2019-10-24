import datetime as dt
import subprocess

import pytest
import schedule

import setup_paths
setup_paths.setupPaths()
import block as block


######################################## UNIT TESTS


def testOneTimeJobDecorator_scheduledJob_returnCancelJobWhenDone():
    scheduledFunction = block.oneTimeJob(lambda x: 0)
    assert scheduledFunction(0) == schedule.CancelJob


def testBlockInternet_startBlocking_executeOSCommands(mocker):
    mockIPRoute = mocker.Mock(name="cmd_route")
    mockIPRoute.stdout = b"""
    default via 10.0.2.2 dev enp0s3 proto dhcp metric 100 
    10.0.2.0/24 dev enp0s3 proto kernel scope link src 10.0.2.15 metric 100 
    169.254.0.0/16 dev enp0s3 scope link metric 1000 
    """
    mockBlock = mocker.Mock(name="cmd_block")
    mockRun = mocker.patch("subprocess.run", side_effect=[mockIPRoute, mockBlock])

    block.blockInternet(10)

    # Check if OS functions have been called
    cmdBlock = ["sudo", "aroundtheclock", "enp0s3", "10.0.2.2", "600"]
    cmdRoute = ["ip", "route"]
    mockRun.assert_any_call(cmdRoute, stdout=subprocess.PIPE)
    mockRun.assert_any_call(cmdBlock)
    assert mockRun.call_count == 2


def testBlockInternet_noIPRouteOutputFromOS_throwOSError(mocker):
    mockIPRoute = mocker.Mock(name="cmd_route")
    mockIPRoute.stdout = b""
    _ = mocker.patch("subprocess.run", return_value=mockIPRoute)

    with pytest.raises(OSError):
        block.blockInternet(10)


######################################## INTEGRATION TESTS


def testOneTimeJobDecorator_runTheOneJobScheduled_logNoNextJob(mocker):
    mockLogging = mocker.patch("block.logging.info")

    scheduledFunction = block.oneTimeJob(lambda x: 0)
    schedule.every().day.at("10:00").do(scheduledFunction, 0)
    schedule.run_all()

    mockLogging.assert_called_with("No next job scheduled!")


def testOneTimeJobDecorator_runTheTwoJobsScheduled_logNextJobTime(mocker):
    mockLogging = mocker.patch("block.logging.info")
    today = dt.date.today()     # Bypassing the need to mock .today()

    scheduledFunction = block.oneTimeJob(lambda x: 0)
    schedule.every().day.at("10:00").do(scheduledFunction, 0)
    schedule.every().day.at("23:30").do(scheduledFunction, 0)
    schedule.jobs[0].run()

    mockLogging.assert_called_with("Next job at {} 23:30:00.".format(today))

