import time
import os

from py_hydropi.lib.iter_utils import avg
from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class Input(ThreadedDaemon):
    # TODO: this may benefit from inheritance and a factory method, possibly force stating input type in config.
    frequency = 1

    def __init__(self, samples=1, value_processor=None):
        super().__init__()

        self._samples = samples
        self._last_value = 0
        if not hasattr(self, '_value'):
            self._value = 0

        if value_processor is not None:
            if value_processor.get('range_percentage'):
                range_percentage = value_processor.get('range_percentage')
                self.rp_min = range_percentage.get('min')
                self.rp_max = range_percentage.get('max')
                self.rp_inverted = range_percentage.get('inverted')
                if self.rp_inverted:
                    self.value_processor = lambda v: 100 - ((v - self.rp_min) / (self.rp_max - self.rp_min)) * 100
                else:
                    self.value_processor = lambda v: ((v - self.rp_min) / (self.rp_max - self.rp_min)) * 100
        else:
            self.value_processor = lambda v: v

    @property
    def temp(self):
        return self.value

    @property
    def value(self):
        if self._value == 0:
            if self._last_value == 0:
                return self._value
            else:
                v = self._last_value
                self._last_value = 0
                return v
        else:
            return self._value

    @staticmethod
    def load_config(pi_timer, config):
        sensors = {}
        for sensor, config in config.items():
            if config.get('type', '').upper() in DHTxxInput.provides:
                for i, val in enumerate(config.get('provides')):
                    sensors['{}.{}'.format(sensor, val)] = DHTxxInput(channel=config.get('channel'), value_index=i).start()
            elif config.get('type', '').upper() in OneWireInput.provides:
                sensors[sensor] = OneWireInput(sensor_id=config.get('sensor_id')).start()
            elif config.get('type', '').replace('-', '_').upper() in UltrasonicInput.provides:
                sensors[sensor] = UltrasonicInput(channels=config.get('channels'), pi_timer=pi_timer, value_processor=config.get('value_processor')).start()
        return sensors

    def _main_loop(self):
        while self._continue:
            self._value = avg([self.value_processor(self._read()) or 0 for i in range(self._samples)])
            time.sleep(self.frequency)

    def _read(self):
        raise NotImplementedError


if os.environ.get('PY_HYDROPI_TESTING') == 'true':
    class Input(Input):
        falling = True
        _temp = 20
        _test_moving_temp = True

        @property
        def temp(self):
            if self._test_moving_temp:
                print(self.__class__.__name__, self._temp)
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
                print(self.__class__.__name__, self._temp)
                if self.falling:
                    if self._temp < 15:
                        self.falling = False
                    self._temp -= 0.1
                    return self._temp
                else:
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

from py_hydropi.lib.modules.sensors.dhtxx import DHTxxInput
from py_hydropi.lib.modules.sensors.one_wire import OneWireInput
from py_hydropi.lib.modules.sensors.hc_sr04 import UltrasonicInput
