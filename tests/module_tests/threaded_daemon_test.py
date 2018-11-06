import time

from py_hydropi.lib.threaded_daemon import ThreadedDaemon
from module_tests.base_test_object import BaseTestObject


class MockThreadedDaemon(ThreadedDaemon):
    def _main_loop(self):
        while self._continue:
            print('looping')
            time.sleep(0.05)


class TestThreadedDaemon(BaseTestObject):
    def test_daemon_stops_cleanly(self):

        self.daemon = MockThreadedDaemon()
        self.daemon.start()
        time.sleep(0.1)
        self.daemon.stop()
        assert not self.daemon._continue

    def test_threaded_daemon_wth_context_manager(self):
        with MockThreadedDaemon() as daemon:
            time.sleep(0.1)
