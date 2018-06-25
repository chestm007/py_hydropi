import time

from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class SensorMetricCollector(ThreadedDaemon):
    def __init__(self, db, reporter):
        super().__init__()
        self.db = db
        self.reporter = reporter

    def _main_loop(self):
        while self._continue:
            self.push_all()
            time.sleep(10)

    def push_all(self):
        for id, sensor in self.db._inputs.items():
            self.reporter.push(id, sensor.value)
