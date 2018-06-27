from multiprocessing import Queue


from py_hydropi.lib.config import ApiConfig, MetricsConfig
from py_hydropi.lib.memdatabase import MemDatabase
from py_hydropi.lib.metrics.collector_controller import MetricCollectorController
from py_hydropi.lib.metrics.collectors.output import OutputMetricCollector
from py_hydropi.lib.metrics.collectors.sensor import SensorMetricCollector
from py_hydropi.lib.modules.inputs import Input
from py_hydropi.lib.modules.threshold_switch import ThresholdSwitch
from py_hydropi.lib.modules.timer import SimpleTimer, ClockTimer

from .lib.API.main import ApiServer

from .lib import Logger, Output, ModuleConfig, GPIO


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

        self.setup_IO()

        if self.metrics_config.enabled:
            self.metrics_controller = MetricCollectorController(
                self.db, self.metrics_config, [
                    SensorMetricCollector, OutputMetricCollector
                ]
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def cleanup(self):
        self.gpio.cleanup()

    def start(self):
        if hasattr(self, 'api'):
            self.api.start()
        for type_ in self.db.controllers.values():
            for name, c in type_.items():
                self.logger.info('Starting controller: {}'.format(name))
                c.start()
        if hasattr(self, 'metrics_controller'):
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

    def stop(self):
        if hasattr(self, 'api'):
            self.api.stop()
        for type_ in self.db.controllers.values():
            for name, c in type_.items():
                self.logger.info('Stopping controller: {}'.format(name))
                c.stop()
        self.cleanup()

    def setup_IO(self):
        sensor_config = self.module_config.config.get('sensors')
        if sensor_config is not None:
            self.db._inputs = Input.load_config(sensor_config)

        clock_config = self.module_config.config.get('clock_timer')
        if clock_config is not None:
            self.db.controllers['clock_timer'] = ClockTimer.load_config(self, clock_config)

        simple_config = self.module_config.config.get('simple_timer')
        if simple_config is not None:
            self.db.controllers['simple_timer'] = SimpleTimer.load_config(self, simple_config)

        threshold_config = self.module_config.config.get('threshold')
        if threshold_config is not None:
            self.db.controllers['threshold'] = ThresholdSwitch.load_config(self, threshold_config)

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
    rpi_timer.stop()
    rpi_timer.cleanup()


if __name__ == '__main__':
    main()
