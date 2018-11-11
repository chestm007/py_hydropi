import time

from py_hydropi.lib.modules.threshold_switch import TargetThresholdSwitch


# noinspection PyTypeChecker
from module_tests.base_test_object import BaseTestObject

_multiprocess_can_split_ = True


class TestThresholdSwitch(BaseTestObject):
    threshold_switch = None

    @classmethod
    def setUpClass(cls):
        cls.input_ = cls.MockInput()
        cls.falling = cls.MockOutput(1)
        cls.rising = cls.MockOutput(2)
        cls.threshold_switch = TargetThresholdSwitch(
            target=20,
            upper=21,
            lower=19,
            input_=cls.input_,
            poll_sec=0.1)

        cls.threshold_switch.set_falling_object(cls.falling)
        cls.threshold_switch.set_rising_object(cls.rising)
        cls.threshold_switch.start()

    def test_when_value_equals_target(self):
        self.input_.value = 20
        time.sleep(0.5)
        self.assertFalse(self.falling.active)
        self.assertFalse(self.rising.active)

    def test_when_value_above_upper(self):
        self.input_.value = 22
        time.sleep(0.5)
        self.assertFalse(self.rising.active)
        self.assertTrue(self.falling.active)

    def test_when_value_below_lower(self):
        self.input_.value = 18
        time.sleep(0.5)
        self.assertFalse(self.falling.active)
        self.assertTrue(self.rising.active)

    @classmethod
    def tearDownClass(cls):
        cls.threshold_switch.stop()
