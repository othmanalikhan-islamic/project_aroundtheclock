import datetime as dt
import unittest

import prayertimes


######################################## UNIT TESTS


class UnitTestPrayerModule(unittest.TestCase):

    def setUp(self):
        self.FORMAT = "%Y-%m-%d %H:%M"

    def testJulianEquation_standardDate_calculateCorrectly(self):
        JD = 2458517.5
        date = dt.datetime(2019, 2, 3)
        self.assertEqual(JD, prayertimes._julianEquation(date))

    def testSunEquation_standardValue_calculateCorrectly(self):
        date = dt.datetime(2019, 1, 1)
        declination = -23.03993184124207
        equationOfTime = -0.053431595269049836
        DEC, EOT = prayertimes._sunEquation(date)
        self.assertEqual(DEC, declination, msg="Declination calculations failed!")
        self.assertEqual(EOT, equationOfTime, msg="EoT calculations failed!")

    def testHorizonEquation_standardValue_calculateCorrectly(self):
        calculated = dt.timedelta(seconds=33298, microseconds=699809)
        ANG = 50.5
        LAT = 26.2172
        DEC = -16.3741
        self.assertEqual(calculated, prayertimes._horizonEquation(ANG, LAT, DEC))

    def testAsrEquation_standardValue_calculateCorrectly(self):
        calculated = dt.timedelta(seconds=14061, microseconds=155471)
        SHA = 2
        LAT = 26.2172
        DEC = -16.3741
        self.assertEqual(calculated, prayertimes._asrEquation(SHA, LAT, DEC))

    def testComputePrayerCronTiming_standardValue_calculateCorrectly(self):
        fajr = dt.datetime.strptime("2019-08-10 03:42", self.FORMAT)
        cronStart = dt.datetime.strptime("2019-08-10 03:37", self.FORMAT)
        cronFinish = dt.datetime.strptime("2019-08-10 03:47", self.FORMAT)

        start, finish = prayertimes._computePrayerCronTiming(fajr, 10)
        self.assertEqual(cronStart, start)
        self.assertEqual(cronFinish, finish)


######################################## INTEGRATION TESTS


class IntegrationTestPrayerModule(unittest.TestCase):

    def setUp(self):
        self.FORMAT = "%Y-%m-%d %H:%M"
        self.coordinates = (50.0000, 26.6000)
        self.timezone = 3

    def testComputeFajr_khobarCity_calculateKhobarFajr(self):
        fajr = dt.datetime.strptime("2019-02-04 05:01", self.FORMAT)

        ANG = 18.5
        LAT = 26.2172
        date = dt.datetime(2019, 2, 4)
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeFajr(date, ANG, LAT, thuhr)
        self.assertAlmostEqualPrayer(prayer, fajr, 3)

    def testComputeThuhr_khobarCity_calculateKhobarThuhr(self):
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)

        TZ = 3
        LON = 50.2083
        date = dt.datetime(2019, 2, 4)
        prayer = prayertimes.computeThuhr(date, LON, TZ)
        self.assertAlmostEqualPrayer(prayer, thuhr, 3)

    def testComputeAsr_khobarCity_calculateKhobarAsr(self):
        asr = dt.datetime.strptime("2019-02-04 15:02", self.FORMAT)

        LAT = 26.2172
        shadowLength = 1
        date = dt.datetime(2019, 2, 4)
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeAsr(date, shadowLength, LAT, thuhr)
        self.assertAlmostEqualPrayer(prayer, asr, 3)

    def testComputeMaghrib_khobarCity_calculateKhobarMaghrib(self):
        maghrib = dt.datetime.strptime("2019-02-04 17:26", self.FORMAT)

        ANG = 0.833
        LAT = 26.2172
        date = dt.datetime(2019, 2, 4)
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeMaghrib(date, LAT, thuhr, angle=ANG)
        self.assertAlmostEqualPrayer(prayer, maghrib, 3)

    def testComputeIshaUmmAlQura_khobarCity_return90MinuteFromMaghrib(self):
        isha = dt.datetime.strptime("2019-02-04 18:56", self.FORMAT)

        maghrib = dt.datetime.strptime("2019-02-04 17:26", self.FORMAT)
        prayer = prayertimes.computeIshaUmmAlQura(maghrib)
        self.assertAlmostEqualPrayer(prayer, isha, 0)   # No error acceptable

    def testComputeIsha_khobarCity_calculateKhobarIsha(self):
        isha = dt.datetime.strptime("2019-02-04 18:29", self.FORMAT)

        ANG = 15.0
        LAT = 26.2172
        date = dt.datetime(2019, 2, 4)
        thuhr = dt.datetime.strptime("2019-02-04 11:53", self.FORMAT)
        prayer = prayertimes.computeIsha(date, ANG, LAT, thuhr)
        self.assertAlmostEqualPrayer(prayer, isha, 3)

    def testComputeAllPrayerTimes_khobarCity20190127_calculatePrecisely(self):
        fajr = dt.datetime.strptime("2019-01-27 05:05", self.FORMAT)
        thuhr = dt.datetime.strptime("2019-01-27 11:53", self.FORMAT)
        asr = dt.datetime.strptime("2019-01-27 14:58", self.FORMAT)
        maghrib = dt.datetime.strptime("2019-01-27 17:19", self.FORMAT)
        isha = dt.datetime.strptime("2019-01-27 18:49", self.FORMAT)

        date = dt.datetime(2019, 1, 27)
        fajrIshaConvention = "umm_alqura"
        asrConvention = "standard"

        prayers = prayertimes.computeAllPrayerTimes(date,
                                                    self.coordinates,
                                                    self.timezone,
                                                    fajrIshaConvention,
                                                    asrConvention)

        self.assertAlmostEqualPrayer(prayers["fajr"], fajr, 2)
        self.assertAlmostEqualPrayer(prayers["thuhr"], thuhr, 2)
        self.assertAlmostEqualPrayer(prayers["asr"], asr, 2)
        self.assertAlmostEqualPrayer(prayers["maghrib"], maghrib, 2)
        self.assertAlmostEqualPrayer(prayers["isha"], isha, 2)

    def testComputeAllPrayerTimes_khobarCity20190207_calculatePrecisely(self):
        fajr = dt.datetime.strptime("2019-02-07 05:00", self.FORMAT)
        thuhr = dt.datetime.strptime("2019-02-07 11:54", self.FORMAT)
        asr = dt.datetime.strptime("2019-02-07 15:05", self.FORMAT)
        maghrib = dt.datetime.strptime("2019-02-07 17:28", self.FORMAT)
        isha = dt.datetime.strptime("2019-02-07 18:58", self.FORMAT)

        date = dt.datetime(2019, 2, 7)
        fajrIshaConvention = "umm_alqura"
        asrConvention = "standard"

        prayers = prayertimes.computeAllPrayerTimes(date,
                                                    self.coordinates,
                                                    self.timezone,
                                                    fajrIshaConvention,
                                                    asrConvention)

        self.assertAlmostEqualPrayer(prayers["fajr"], fajr, 2)
        self.assertAlmostEqualPrayer(prayers["thuhr"], thuhr, 2)
        self.assertAlmostEqualPrayer(prayers["asr"], asr, 2)
        self.assertAlmostEqualPrayer(prayers["maghrib"], maghrib, 2)
        self.assertAlmostEqualPrayer(prayers["isha"], isha, 2)

    def testComputeAllPrayerTimes_khobarCity20190210_calculatePrecisely(self):
        fajr = dt.datetime.strptime("2019-02-10 04:59", self.FORMAT)
        thuhr = dt.datetime.strptime("2019-02-10 11:54", self.FORMAT)
        asr = dt.datetime.strptime("2019-02-10 15:06", self.FORMAT)
        maghrib = dt.datetime.strptime("2019-02-10 17:29", self.FORMAT)
        isha = dt.datetime.strptime("2019-02-10 18:59", self.FORMAT)

        date = dt.datetime(2019, 2, 10)
        fajrIshaConvention = "umm_alqura"
        asrConvention = "standard"

        prayers = prayertimes.computeAllPrayerTimes(date,
                                                    self.coordinates,
                                                    self.timezone,
                                                    fajrIshaConvention,
                                                    asrConvention)

        self.assertAlmostEqualPrayer(prayers["fajr"], fajr, 1)
        self.assertAlmostEqualPrayer(prayers["thuhr"], thuhr, 1)
        self.assertAlmostEqualPrayer(prayers["asr"], asr, 2)
        self.assertAlmostEqualPrayer(prayers["maghrib"], maghrib, 2)
        self.assertAlmostEqualPrayer(prayers["isha"], isha, 2)

    def testComputeAllPrayerTimes_khobarCity20190810_calculatePrecisely(self):
        fajr = dt.datetime.strptime("2019-08-10 03:42", self.FORMAT)
        thuhr = dt.datetime.strptime("2019-08-10 11:46", self.FORMAT)
        asr = dt.datetime.strptime("2019-08-10 15:16", self.FORMAT)
        maghrib = dt.datetime.strptime("2019-08-10 18:21", self.FORMAT)
        isha = dt.datetime.strptime("2019-08-10 19:51", self.FORMAT)

        date = dt.datetime(2019, 8, 10)
        fajrIshaConvention = "umm_alqura"
        asrConvention = "standard"

        prayers = prayertimes.computeAllPrayerTimes(date,
                                                    self.coordinates,
                                                    self.timezone,
                                                    fajrIshaConvention,
                                                    asrConvention)

        self.assertAlmostEqualPrayer(prayers["fajr"], fajr, 2)
        self.assertAlmostEqualPrayer(prayers["thuhr"], thuhr, 2)
        self.assertAlmostEqualPrayer(prayers["asr"], asr, 2)
        self.assertAlmostEqualPrayer(prayers["maghrib"], maghrib, 2)
        self.assertAlmostEqualPrayer(prayers["isha"], isha, 2)

    def assertAlmostEqualPrayer(self, p1, p2, err):
        """
        Tests whether the two prayer times are almost equal by checking whether
        they differ by the given amount of minutes.

        :param p1: datetime.datetime, the time of the first prayer.
        :param p2: datetime.datetime, the time of the second prayer.
        :param err: Integer, the number of minutes the prayer can deviate.
        :return: Boolean, true if test succeeds otherwise false.
        """
        hours, minutes, seconds = prayertimes.computeDiff(p1, p2)
        if abs(60*hours + minutes + seconds/60) > err:
            self.fail("Prayer time differs by {:02d}:{:02d}:{:02d}!\np1: {}\np2: {}"
                      .format(hours, minutes, seconds, p1, p2))

