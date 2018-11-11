import time

from py_hydropi.lib.modules.timer import SimpleTimer
from module_tests.base_test_object import BaseTestObject
_multiprocess_can_split_ = True


class TestSimpleTimer(BaseTestObject):
    simpletimer = None

    @classmethod
    def setUpClass(cls):
        cls.output = cls.MockOutput(1)
        cls.simpletimer = SimpleTimer(on_time='1s', off_time='1s')
        cls.simpletimer.attach_object(cls.output)
        cls.simpletimer.start()
        time.sleep(0.2)

    def test_intervals(self):
        if self.output.active:
            time.sleep(1)

        for i in range(2):
            self.assertFalse(self.output.active)
            time.sleep(1)
            self.assertTrue(self.output.active)
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.simpletimer.stop()
