import datetime
import json

from py_hydropi.lib.modules.timer import ClockTimer
from module_tests.base_test_object import BaseTestObject


class TestClockTimer(BaseTestObject):
    def setUp(self):
        self.output = self.MockOutput(1)
        self.clock_timer = ClockTimer('1:00am - 4:00am')
        self.clock_timer.attach_object(self.output)
        self.current_hour = 0

        def get_current_time():
            now = datetime.datetime.now()
            return datetime.datetime(now.year, now.month, now.day, self.current_hour)
        self.clock_timer._get_current_time = get_current_time

    def test_now_after_daytime_active(self):
        self.clock_timer.on_time = '3:00am'
        self.clock_timer.off_time = '4:00pm'
        self.current_hour = 17
        # negligible bug in code means outputs must be activated initially before deactivation can occur
        self.clock_timer._check_timer()
        self.assertFalse(self.output.active)

    def test_now_before_daytime_active(self):
        self.clock_timer.on_time = '3:00am'
        self.clock_timer.off_time = '4:00pm'
        self.current_hour = 1
        self.clock_timer._check_timer()
        self.clock_timer._check_timer()
        self.clock_timer._check_timer()
        self.assertFalse(self.output.active)

    def test_now_during_daytime_active(self):
        self.clock_timer.on_time = '3:00am'
        self.clock_timer.off_time = '4:00pm'
        self.current_hour = 4
        self.clock_timer._check_timer()
        self.clock_timer._check_timer()
        self.clock_timer._check_timer()
        self.assertTrue(self.output.active)

    def test_now_overnight_active_4pm_3am(self):
        self.clock_timer.on_time = '4:00pm'
        self.clock_timer.off_time = '3:00am'
        for i in range(3):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertTrue(self.output.active, msg=i)
        for i in range(3, 16):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertFalse(self.output.active, msg=i)
        for i in range(16, 24):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertTrue(self.output.active, msg=i)
        for i in range(3):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertTrue(self.output.active, msg=i)

    def test_now_overnight_active_4pm_10am(self):
        self.clock_timer.on_time = '4:00pm'
        self.clock_timer.off_time = '10:00am'
        for i in range(10):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertTrue(self.output.active, msg=i)
        for i in range(10, 16):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertFalse(self.output.active, msg=i)
        for i in range(16, 24):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertTrue(self.output.active, msg=i)
        for i in range(10):
            self.current_hour = i
            self.clock_timer._check_timer()
            self.assertTrue(self.output.active, msg=i)

    def test_now_during_day_before_overnight_activation(self):
        self.clock_timer.on_time = '4:00pm'
        self.clock_timer.off_time = '3:00am'
        self.current_hour = 17
        self.clock_timer._check_timer()
        self.assertTrue(self.output.active)

    def test_now_during_morning_after_overnight_activation(self):
        self.clock_timer.on_time = '4:00pm'
        self.clock_timer.off_time = '3:00am'
        self.current_hour = 2
        self.clock_timer._check_timer()
        self.assertTrue(self.output.active)

    def test_json_serialization(self):
        print(json.dumps(self.clock_timer.to_json()))
