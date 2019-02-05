import datetime as dt
import unittest

import prayertimes


class TestPrayerModule(unittest.TestCase):

    def setUp(self):
        self.FORMAT = "%Y-%m-%d %H:%M"

    def testComputeJulianDay_standardDate_convertedDateToFloat(self):
        JD = 2458517.5
        self.assertEqual(JD, prayertimes.computeJulianDay(2019, 2, 3))

    def testComputeSun_standardValue_returnCalculatedValue(self):
        declination = -23.03993184124207
        equationOfTime = -0.053431595269049836
        DEC, EOT = prayertimes.computeSun(2019, 1, 1)
        self.assertEqual(DEC, declination, msg="Declination calculations failed!")
        self.assertEqual(EOT, equationOfTime, msg="EoT calculations failed!")

    def testT_standardValue_returnCalculatedValue(self):
        calculated = dt.timedelta(seconds=33298, microseconds=699809)
        ANG = 50.5
        LAT = 26.2172
        DEC = -16.3741
        self.assertEqual(calculated, prayertimes.horizonEquation(ANG, LAT, DEC))

    def testComputeFajr(self):
        ANG = 18.5
        LAT = 26.2172
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        fajr = dt.datetime.strptime("2019-02-04 05:01", self.FORMAT)

        DEC, _ = prayertimes.computeSun(2019, 2, 4)
        prayer = prayertimes.computeFajr(thuhr, ANG, LAT, DEC, prayertimes.horizonEquation)
        self.assertAlmostEqualPrayer(fajr, prayer, 3)

    # def testComputeThuhr(self):
    #     TZ = 3
    #     LON = 50.2083
    #     LAT = 26.2172
    #     DEC, EQT = prayertimes.computeSun(2019, 2, 4)
    #     thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
    #
    #     prayer = prayertimes.computeThuhr(LON, LAT, EQT, TZ)
    #     self.assertAlmostEqualPrayer(prayer, thuhr, 0)

    def assertAlmostEqualPrayer(self, p1, p2, err):
        """
        Tests whether the two prayer times are almost equal by:
            Check

        :param p1: datetime.datetime, the time of the first prayer.
        :param p2: datetime.datetime, the time of the second prayer.
        :param error: Integer, the number of minutes the prayer can deviate.
        :return: Boolean, true if test succeeds otherwise false.
        """
        diff = p2 - p1
        hours, _ = divmod(diff.total_seconds(), 3600)
        minutes, _ = divmod(diff.total_seconds(), 60)

        if abs(minutes) > err:
            self.fail("Prayer time differs by {}!".format(diff))
