import time
from threading import Thread

from py_hydropi.lib.metrics.reporters import reporter_factory
from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class MetricCollectorController(ThreadedDaemon):
    def __init__(self, db, config, collectors: list):
        super().__init__()
        self.db = db
        self.config = config.config
        self.reporter = reporter_factory(self.config.get('reporter'))
        self.frequency = self.config.get('frequency', 10)
        self.collectors = [self._init_collector(c) for c in collectors]

    def add_collector(self, collector):
        self.collectors.append(collector(self.db, self.reporter))

    def _init_collector(self, collector):
        self.logger.debug('initializing collector: {}'.format(collector.__name__))
        return collector(self.db, self.reporter)

    def _main_loop(self):
        while self._continue:
            thread_pool = []
            for c in self.collectors:
                for id_, value in c.push_all():
                    t = Thread(target=self.reporter.push, args=[self.log_result, id_, value])
                    thread_pool.append(t)
                    t.start()
            for t in thread_pool:
                t.join()
            time.sleep(self.frequency)

    def log_result(self, res):
        self.logger.error('Metrics report returned status:{} reason:{}'.format(*res))
