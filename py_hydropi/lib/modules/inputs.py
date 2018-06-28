import time
import Adafruit_DHT
import os

from py_hydropi.lib.iter_utils import avg
from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class Input(ThreadedDaemon):
    _parsers = {'28-041752029bff': lambda i: int(i.splitlines()[1].split('t=')[1]) / 1000.0}
    _path = '/sys/bus/w1/devices'
    _sensor_template = '{path}/{sensor_id}/w1_slave'

    def __init__(self, sensor_id=None, channel=None, value_index=None, channels=None, samples=1, pi_timer=None):
        super().__init__()
        assert channels or sensor_id or (channel is not None and value_index is not None)
        assert channels is None or sensor_id is None or (channel is None and value_index is None)

        if sensor_id:
            self._read = self._read_file
        elif channel:
            self._read = self._read_channel
        elif channels:
            self.gpio = pi_timer.gpio
            self._read = self._read_channels
            self.gpio.set_output_on(channels.get('out'))
            self.gpio.setup_input_channel(channels.get('in'))
            self.gpio._GPIO.output(channels.get('out'), False)

        self.sensor_id = sensor_id
        self._samples = samples
        self.channels = channels
        self.channel = channel
        self.value_index = value_index
        if not hasattr(self, 'value'):
            self.value = 0
        self._sensor_path = self._sensor_template.format(path=self._path,
                                                         sensor_id=self.sensor_id)

    @property
    def temp(self):
        return self.value

    @staticmethod
    def load_config(pi_timer, config):
        sensors = {}
        for sensor, config in config.items():
            if config.get('channel'):
                for i, val in enumerate(config.get('provides')):
                    sensors['{}.{}'.format(sensor, val)] = Input(channel=config.get('channel'), value_index=i).start()
            elif config.get('sensor_id'):
                sensors[sensor] = Input(sensor_id=config.get('sensor_id')).start()
            elif config.get('channels'):
                sensors[sensor] = Input(channels=config.get('channels'), pi_timer=pi_timer).start()
        return sensors

    def _main_loop(self):
        while self._continue:
            self.value = avg([self._read() or 0 for i in range(self._samples)])
            time.sleep(1)

    def _read_channels(self):
        pulse_end, pulse_start = [None]*2

        while self.gpio._GPIO.input(self.channels.get('in')) == 0:
            pulse_start = time.time()

        while self.gpio._GPIO.input(self.channels.get('in')) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150

        return round(distance, 2)

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

if os.environ.get('PY_HYDROPI_TESTING') == 'true':
    class Input(Input):
        falling = True
        _temp = 20
        _test_moving_temp = True

        @property
        def temp(self):
            if self._test_moving_temp:
                print(self.channel or self.sensor_id, self._temp)
                if self.falling:
                    if self._temp < 15:
                        self.falling = False
                    self._temp -= 0.1
                    return self._temp
                if not self.falling:
                    if self._temp > 25:
                        self.falling = True
                    self._temp += 0.1
                    return self._temp
            else:
                return 20
        @property
        def value(self):
            if self._test_moving_temp:
                print(self.channel or self.sensor_id, self._temp)
                if self.falling:
                    if self._temp < 15:
                        self.falling = False
                    self._temp -= 0.1
                    return self._temp
                if not self.falling:
                    if self._temp > 25:
                        self.falling = True
                    self._temp += 0.1
                    return self._temp
            else:
                return 20

        def _main_loop(self):
            time.sleep(10)
            return

        def start(self):
            return self

