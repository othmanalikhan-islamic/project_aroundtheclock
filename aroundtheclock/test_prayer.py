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
        DEC, EOT = prayertimes._sunEquation(2019, 1, 1)
        self.assertEqual(DEC, declination, msg="Declination calculations failed!")
        self.assertEqual(EOT, equationOfTime, msg="EoT calculations failed!")

    def testT_standardValue_returnCalculatedValue(self):
        calculated = dt.timedelta(seconds=33298, microseconds=699809)
        ANG = 50.5
        LAT = 26.2172
        DEC = -16.3741
        self.assertEqual(calculated, prayertimes._horizonEquation(ANG, LAT, DEC))

    def testComputeFajr_khobarParams_returnKhobarFajr(self):
        fajr = dt.datetime.strptime("2019-02-04 05:01", self.FORMAT)

        ANG = 18.5
        LAT = 26.2172
        year, month, day = 2019, 2, 4
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeFajr(year, month, day, ANG, LAT, thuhr,
                                         prayertimes._horizonEquation,
                                         prayertimes._sunEquation)
        self.assertAlmostEqualPrayer(prayer, fajr, 3)

    def testComputeThuhr_khobarParams_returnKhobarThuhr(self):
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)

        TZ = 3
        LON = 50.2083
        year, month, day = 2019, 2, 4
        prayer = prayertimes.computeThuhr(year, month, day, LON, TZ, prayertimes._sunEquation)
        self.assertAlmostEqualPrayer(prayer, thuhr, 3)

    def testComputeAsr_khobarParams_returnKhobarAsr(self):
        asr = dt.datetime.strptime("2019-02-04 15:02", self.FORMAT)

        LAT = 26.2172
        shadowLength = 1
        year, month, day = 2019, 2, 4
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeAsr(year, month, day, shadowLength, LAT, thuhr,
                                        prayertimes._asrEquation,
                                        prayertimes._sunEquation)
        self.assertAlmostEqualPrayer(prayer, asr, 3)

    def testComputeMaghrib_khobarParams_returnKhobarMaghrib(self):
        maghrib = dt.datetime.strptime("2019-02-04 17:26", self.FORMAT)

        ANG = 0.833
        LAT = 26.2172
        year, month, day = 2019, 2, 4
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeMaghrib(year, month, day, ANG, LAT, thuhr,
                                            prayertimes._horizonEquation,
                                            prayertimes._sunEquation)
        self.assertAlmostEqualPrayer(prayer, maghrib, 3)

    def assertAlmostEqualPrayer(self, p1, p2, err):
        """
        Tests whether the two prayer times are almost equal by:
            Check

        :param p1: datetime.datetime, the time of the first prayer.
        :param p2: datetime.datetime, the time of the second prayer.
        :param error: Integer, the number of minutes the prayer can deviate.
        :return: Boolean, true if test succeeds otherwise false.
        """

        if p2 > p1:
            diff = p2 - p1
        else:
            diff = p1 - p2

        hours, remainder = divmod(diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        if abs(minutes) > err:
            self.fail("Prayer time differs by {:02d}:{:02d}:{:02d}!\np1: {}\np2: {}"
                      .format(hours, minutes, seconds, p1, p2))
