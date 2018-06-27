import time
import Adafruit_DHT

from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class Input(ThreadedDaemon):
    _parsers = {'28-041752029bff': lambda i: int(i.splitlines()[1].split('t=')[1]) / 1000.0}
    _path = '/sys/bus/w1/devices'
    _sensor_template = '{path}/{sensor_id}/w1_slave'

    def __init__(self, sensor_id=None, channel=None, value_index=None):
        super().__init__()
        print(channel, value_index)
        assert sensor_id or (channel is not None and value_index is not None)
        assert sensor_id is None or (channel is None and value_index is None)

        if sensor_id:
            self._read = self._read_file
        elif channel:
            self._read = self._read_channel

        self.sensor_id = sensor_id
        self.channel = channel
        self.value_index = value_index
        self.value = 0
        self._sensor_path = self._sensor_template.format(path=self._path,
                                                         sensor_id=self.sensor_id)

    @property
    def temp(self):
        return self.value

    @staticmethod
    def load_config(config):
        sensors = {}
        for sensor, config in config.items():
            for i, val in enumerate(config.get('provides')):
                sensors['{}.{}'.format(sensor, val)] = Input(channel=config.get('channel'), value_index=i).start()
        return sensors

    def _main_loop(self):
        while self._continue:
            self.value = self._read() or 0
            time.sleep(1)

    def _read_channel(self):
        val = None
        try:
            val = Adafruit_DHT.read_retry(11, self.channel)
            val = val[self.value_index]
        except IndexError:
            self.logger.error('error processing response from sensor channel {}({})'.format(
                self.channel, self.value_index))
        except Exception:
            self.logger.error('error reading from {}: channel {}({})'.format(
                self.__class__.__name__, self.channel, self.value_index))
        return val

    def _read_file(self):
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
