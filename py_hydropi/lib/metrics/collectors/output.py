import time

from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class OutputMetricCollector(ThreadedDaemon):
    def __init__(self, db, reporter):
        super().__init__()
        self.db = db
        self.reporter = reporter

    def _main_loop(self):
        while self._continue:
            self.push_all()
            time.sleep(10)

    def push_all(self):
        for type_, group_dict in self.db.controllers.items():
            outputs = []

            for group, controller in group_dict.items():
                if hasattr(controller, 'attached_triggered_outputs'):
                    for d in controller.attached_triggered_outputs.values():
                        outputs.extend(d.get('objects'))
                outputs.extend(controller.attached_outputs)

                for output in outputs:
                    self.reporter.push(
                        'channel{channel}activated'.format(channel=output.channel),
                        int(output.state)
                    )
