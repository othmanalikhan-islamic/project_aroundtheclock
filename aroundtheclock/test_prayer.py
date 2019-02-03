import unittest
from datetime import datetime as dt

import prayertimes
from math import radians


class TestPrayerModule(unittest.TestCase):

    def setUp(self):
        self.FORMAT = "%Y-%m-%d %H:%M"
        self.LAT = radians(26.2172)
        self.LON = radians(50.1971)

    def testComputeJulianDay(self):
        jd = 2458517.5
        self.assertEqual(jd, prayertimes.computeJulianDay(2019, 2, 3))

    @unittest.skip
    def testComputeFajr(self):
        angle = radians(18.5)
        thuhr = dt.strptime("2019-01-01 11:53", self.FORMAT)
        fajr = dt.strptime("2019-01-01 05:01", self.FORMAT)

        D, _ = prayertimes.Julian(2019, 1, 1)

        prayer = prayertimes.computeFajr(thuhr, angle, self.LAT, D, prayertimes.T)
        self.assertAlmostEqualPrayer(prayer, fajr, 5)

    def assertAlmostEqualPrayer(self, p1, p2, error):
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
        self.assertEqual(hours, 0)
        self.assertTrue(abs(minutes) <= error)
