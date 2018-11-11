import time
import uuid

import nose

from py_hydropi.lib.threaded_daemon import ThreadedDaemon
from module_tests.base_test_object import BaseTestObject


class TestThreadedDaemon(BaseTestObject):
    @classmethod
    def setUpClass(cls):
        cls.output = []

        def log_loop(self):
            while self._continue:
                cls.output.append('looped')

        ThreadedDaemon._main_loop = log_loop

    def test_daemon_stops_cleanly(self):

        self.daemon = ThreadedDaemon().start()
        while len(self.output) < 20:
            time.sleep(0.1)
        self.daemon.stop()
        self.assertFalse(self.daemon._continue)
        self.assertIn('looped', self.output)

    def test_threaded_daemon_wth_context_manager(self):
        with ThreadedDaemon() as daemon:
            while len(self.output) < 20:
                time.sleep(0.1)
            self.assertTrue(daemon._continue)
        self.assertIn('looped', self.output)

    def tearDown(self):
        self.output.clear()
