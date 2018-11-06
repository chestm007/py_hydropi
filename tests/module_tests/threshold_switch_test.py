import time

from py_hydropi.lib.modules.threshold_switch import TargetThresholdSwitch


# noinspection PyTypeChecker
from module_tests.base_test_object import BaseTestObject


class TestThresholdSwitch(BaseTestObject):
    def setup(self):
        self.input_ = self.MockInput()
        self.falling = self.MockOutput(1)
        self.rising = self.MockOutput(2)
        self.threshold_switch = TargetThresholdSwitch(
            target=20,
            upper=21,
            lower=19,
            input_=self.input_,
            poll_sec=0.1)

        self.threshold_switch.set_falling_object(self.falling)
        self.threshold_switch.set_rising_object(self.rising)
        self.threshold_switch.start()

    def test_when_value_equals_target(self):
        self.input_.value = 20
        time.sleep(0.5)
        assert not self.falling.active
        assert not self.rising.active

    def test_when_value_above_upper(self):
        self.input_.value = 22
        time.sleep(0.5)
        assert not self.rising.active
        assert self.falling.active

    def test_when_value_below_lower(self):
        self.input_.value = 18
        time.sleep(0.5)
        assert not self.falling.active
        assert self.rising.active

    def teardown(self):
        self.threshold_switch.stop()

