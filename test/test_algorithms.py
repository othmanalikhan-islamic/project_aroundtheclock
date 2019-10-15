import datetime as dt

import setup_paths
setup_paths.setupPaths()
import algorithms


######################################## UNIT TESTS


def testJulianEquation_standardDate_calculateCorrectly():
    JD = 2458517.5
    date = dt.datetime(2019, 2, 3)
    assert JD == algorithms.julianEquation(date)


def testSunEquation_standardValue_calculateCorrectly():
    date = dt.datetime(2019, 1, 1)
    DEC = -23.03993184124207
    EOT = -0.053431595269049836
    declination, equationOfTime = algorithms.sunEquation(date)
    assert DEC == declination, "Declination calculations failed!"
    assert EOT == equationOfTime, "EoT calculations failed!"


def testHorizonEquation_standardValue_calculateCorrectly():
    calculated = dt.timedelta(seconds=33298, microseconds=699809)
    ANG = 50.5
    LAT = 26.2172
    DEC = -16.3741
    assert calculated == algorithms.horizonEquation(ANG, LAT, DEC)


def testAsrEquation_standardValue_calculateCorrectly():
    calculated = dt.timedelta(seconds=14061, microseconds=155471)
    SHA = 2
    LAT = 26.2172
    DEC = -16.3741
    assert calculated == algorithms.asrEquation(SHA, LAT, DEC)
