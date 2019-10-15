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
    mockIPRoute = mocker.Mock(name="ip route")
    mockIPRoute.stdout = b"""
    default via 10.0.2.2 dev enp0s3 proto dhcp metric 100 
    10.0.2.0/24 dev enp0s3 proto kernel scope link src 10.0.2.15 metric 100 
    169.254.0.0/16 dev enp0s3 scope link metric 1000 
    """

    mockSubprocess = mocker.patch("subprocess.run", return_value=mockIPRoute)
    arpPoison = ["timeout", "600", "sudo", "arpspoof", "-i", "enp0s3", "10.0.2.2"]
    kwargs = {"timeout": 600}

    block.blockInternet(10)
    mockSubprocess.assert_called_with(arpPoison, **kwargs)


def testBlockInternet_stopBlocking_returnTimeout(mocker):
    calls = [mocker.MagicMock(name="ip route"), subprocess.TimeoutExpired("", 0)]
    mockSubprocess = mocker.patch("subprocess.run", side_effect=calls)

    try:
        block.blockInternet(10)
        assert mockSubprocess.call_count == 2
    except subprocess.TimeoutExpired:
        pytest.fail("TimeoutExpired exception was raised when it shouldn't!")

