from threading import Thread

import time

from ..logger import Logger


class Input:
    _parsers = {'28-041752029bff': lambda i: int(i.splitlines()[1].split('t=')[1]) / 1000.0}
    _path = '/sys/bus/w1/devices'
    _sensor_template = '{path}/{sensor_id}/w1_slave'

    def __init__(self, sensor_id):
        self.logger = Logger(self.__class__.__name__)
        self.sensor_id = sensor_id
        self.temp = 0
        self._continue = False
        self._thread = None
        self._sensor_path = self._sensor_template.format(path=self._path,
                                                         sensor_id=self.sensor_id)

    def start(self):
        self._continue = True
        self._thread = Thread(target=self._main_loop)
        self._thread.start()
        return self

    def stop(self):
        self._continue = False

    def _main_loop(self):
        while self._continue:
            self.temp = self._read() or 0
            time.sleep(1)

    def _read(self):
        try:
            with open(self._sensor_path) as s:
                try:
                    return self._parsers[self.sensor_id](s.read())
                except:
                    self.logger.error('error reading sensor data')
                    return

        except FileNotFoundError:
            self.logger.error('specified sensor not found: {}\nexiting monitoing thread'.format(self._sensor_path))
            self.stop()
