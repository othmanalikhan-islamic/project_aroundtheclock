import unittest
import datetime as dt
from pprint import pprint

import prayertimes
from math import radians


class TestPrayerModule(unittest.TestCase):

    def setUp(self):
        self.FORMAT = "%Y-%m-%d %H:%M"
        self.LAT = radians(26.2172)
        self.LON = radians(50.1971)

    def testComputeJulianDay_standardDate_convertedDateToFloat(self):
        jd = 2458517.5
        self.assertEqual(jd, prayertimes.computeJulianDay(2019, 2, 3))

    def testComputeSun_standardValue_returnCalculatedValue(self):
        # declination = -16.668351110659202
        # equationOfTime = -0.22864750125837574
        declination = -23.03993184124207
        equationOfTime = -0.053431595269049836
        D, EoT = prayertimes.computeSun(2019, 1, 1)
        self.assertEqual(D, declination, msg="Declination calculations failed!")
        self.assertEqual(EoT, equationOfTime, msg="EoT calculations failed!")

    def testT_standardValue_returnCalculatedValue(self):
        calculated = dt.timedelta(hours=6.146957845647092)
        angle = -18.5
        LAT = 26.2172
        DEC = 50.1971
        self.assertEqual(calculated, prayertimes.T(angle, LAT, DEC))

    @unittest.skip
    def testComputeFajr(self):
        angle = radians(-18.5)
        thuhr = dt.datetime.strptime("2019-01-01 11:53", self.FORMAT)
        fajr = dt.strptime("2019-01-01 05:01", self.FORMAT)

        D, _ = prayertimes.computeSun(2019, 1, 1)
        prayer = prayertimes.computeFajr(thuhr, angle, self.LAT, D, prayertimes.T)
        pprint(prayer)

        self.assertAlmostEqualPrayer(fajr, prayer, 5)

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
        self.assertEqual(hours, 0, msg="Prayer time differs in hours!")
        self.assertTrue(abs(minutes) <= err, msg="Prayer time differs by more than {} min!".format(err))
