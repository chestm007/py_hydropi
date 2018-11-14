import signal
import sys

from multiprocessing import Queue

import time

from py_hydropi.lib.config import ApiConfig, MetricsConfig
from py_hydropi.lib.iter_utils import JSONableDict
from py_hydropi.lib.memdatabase import MemDatabase
from py_hydropi.lib.metrics.collector_controller import MetricCollectorController
from py_hydropi.lib.metrics.collectors.output import OutputMetricCollector
from py_hydropi.lib.metrics.collectors.sensor import SensorMetricCollector
from py_hydropi.lib.modules.inputs import Input
from py_hydropi.lib.modules.threshold_switch import ThresholdSwitch
from py_hydropi.lib.modules.timer import SimpleTimer, ClockTimer


from py_hydropi.lib import Logger, Output, ModuleConfig, GPIO
from py_hydropi.lib.API.main import ApiServer


class RaspberryPiTimer(object):
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.gpio = GPIO()
        self.queue = Queue()
        self.db = MemDatabase(self.queue)
        self.db.gpio = self.gpio

        self.module_config = ModuleConfig()
        self.api_config = ApiConfig()
        self.metrics_config = MetricsConfig()

        if self.api_config.start:
            self.api = ApiServer(self.db, self.api_config)

        self.setup_io()

        if self.metrics_config.enabled:
            self.metrics_controller = MetricCollectorController(
                self.db, self.metrics_config, [
                    SensorMetricCollector, OutputMetricCollector
                ]
            )
        signal.signal(signal.SIGINT, self.stop)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def cleanup(self):
        self.gpio.cleanup()

    def start(self):
        self.logger.info('starting all services')
        if hasattr(self, 'api'):
            self.logger.info('starting API...')
            self.api.start()

        self.logger.info('starting controllers...')
        for type_ in self.db.controllers.values():
            for name, c in type_.items():
                self.logger.info('Starting controller: {}'.format(name))
                c.start()
        if hasattr(self, 'metrics_controller'):
            self.logger.info('starting metrics reporting...')
            self.metrics_controller.start()

        self._queue_loop()

    def _queue_loop(self):
        while True:
            try:
                recv_req = self.queue.get()
                if recv_req == 'exit':
                    self.logger.info('recieved exit command. shutting down services.')
                    break
            except KeyboardInterrupt:
                self.logger.info('Detected KeyboardInterupt in queue loop, exiting gracefully')
                self.stop()
                break

    def stop(self, *_):
        self.logger.info('stopping all services')
        if hasattr(self, 'api'):
            self.logger.info('Shutting down API server')
            self.api.stop()

        for type_ in self.db.controllers.values():
            for name, c in type_.items():
                self.logger.info('Stopping controller: {}'.format(name))
                c.stop()

        if hasattr(self, 'metrics_controller'):
            self.logger.info('Shutting down metrics collector.')
            self.metrics_controller.stop()

        self.logger.info('Terminating input reader loops.')
        for sensor in self.db.inputs.values():
            sensor.stop()

        self.cleanup()
        self.logger.info('system shutdown complete')

    def setup_io(self):
        self.logger.info('loading sensors...')
        sensor_config = self.module_config.config.get('sensors')
        if sensor_config is not None:
            self.db._inputs = Input.load_config(self, sensor_config)
            for sensor in self.db.inputs.values():
                sensor.start()

        self.logger.info('loading timers...')
        clock_config = self.module_config.config.get('clock_timer')
        if clock_config is not None:
            self.db.controllers['clock_timer'] = JSONableDict(ClockTimer.load_config(self, clock_config))

        simple_config = self.module_config.config.get('simple_timer')
        if simple_config is not None:
            self.db.controllers['simple_timer'] = JSONableDict(SimpleTimer.load_config(self, simple_config))

        self.logger.info('loading switches...')
        threshold_config = self.module_config.config.get('threshold')
        if threshold_config is not None:
            self.db.controllers['threshold'] = JSONableDict(ThresholdSwitch.load_config(self, threshold_config))

        triggered_config = self.module_config.config.get('triggered')
        if triggered_config is not None:
            for group, group_settings in triggered_config.items():
                parent_controller, parent_group = group_settings.get('object').split('.')
                parent_controller = self.db.controllers.get(parent_controller)
                if parent_controller:
                    parent_group = parent_controller.get(parent_group)
                    if parent_group:
                        parent_group.attach_triggered_object(
                            obj=[Output(self, chan)
                                 for chan in group_settings.get('channels')],
                            group_name=group,
                            before=group_settings.get('before'),
                            after=group_settings.get('after'))
                        continue
                self.logger.error('error binding trigger: {}'.format(group))


def main():
    rpi_timer = RaspberryPiTimer()
    rpi_timer.start()


if __name__ == '__main__':
    main()
