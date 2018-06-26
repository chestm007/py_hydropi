import time

from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class MetricCollectorController(ThreadedDaemon):
    def __init__(self, db, reporter, collectors: list):
        super().__init__()
        self.db = db
        self.reporter = reporter
        self.frequency = 10
        self.collectors = [self._init_collector(c) for c in collectors]

    def add_collector(self, collector):
        self.collectors.append(collector(self.db, self.reporter))

    def _init_collector(self, collector):
        self.logger.debug('initializing collector: {}'.format(collector.__name__))
        return collector(self.db, self.reporter)

    def _main_loop(self):
        while self._continue:
            for c in self.collectors:
                c.push_all()
            time.sleep(self.frequency)
