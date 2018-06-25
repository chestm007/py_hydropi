import time

from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class Input(ThreadedDaemon):
    _parsers = {'28-041752029bff': lambda i: int(i.splitlines()[1].split('t=')[1]) / 1000.0}
    _path = '/sys/bus/w1/devices'
    _sensor_template = '{path}/{sensor_id}/w1_slave'

    def __init__(self, sensor_id):
        super().__init__()
        self.sensor_id = sensor_id
        self.value = 0
        self._sensor_path = self._sensor_template.format(path=self._path,
                                                         sensor_id=self.sensor_id)

    @property
    def temp(self):
        return self.value

    def _main_loop(self):
        while self._continue:
            self.value = self._read() or 0
            time.sleep(1)

    def _read(self):
        try:
            with open(self._sensor_path) as s:
                try:
                    return self._parsers[self.sensor_id](s.read())

                except KeyError:
                    self.logger.error('parser not defined for: {}'.format(self.sensor_id))

                except IndexError:
                    self.logger.error('error reading sensor data')
                    return

        except FileNotFoundError:
            self.logger.error('specified sensor not found: {}\nexiting monitoing thread'.format(self._sensor_path))
            self.stop()
