import time

from py_hydropi.lib.modules.timer import SimpleTimer


class DO:

    def __init__(self, channel):
        self.channel = channel
        self.active = False
        self.manual_control = False

    def activate(self):
        self.active = True
        print('activate {}'.format(self.channel))

    def deactivate(self):
        self.active = False
        print('deacivate {}'.format(self.channel))


class TestSimpleTimer:
    def setup(self):
        self.output = DO(1)
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

