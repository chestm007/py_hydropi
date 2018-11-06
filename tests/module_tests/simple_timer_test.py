import time

from py_hydropi.lib.modules.timer import SimpleTimer
from module_tests.base_test_object import BaseTestObject


class TestSimpleTimer(BaseTestObject):
    def setup(self):
        self.output = self.MockOutput(1)
        self.simpletimer = SimpleTimer(on_time='1s', off_time='1s')
        self.simpletimer.attach_object(self.output)
        self.simpletimer.start()
        time.sleep(0.2)

    def test_intervals(self):
        if self.output.active:
            time.sleep(1)

        for i in range(5):
            assert not self.output.active
            time.sleep(1)
            assert self.output.active
            time.sleep(1)

    def teardown(self):
        self.simpletimer.stop()

