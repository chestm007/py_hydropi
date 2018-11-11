import time
import os

from py_hydropi.lib.iter_utils import avg
from py_hydropi.lib.threaded_daemon import ThreadedDaemon


class Input(ThreadedDaemon):
    frequency = 60

    def __init__(self, samples=1, value_processor=None, **kwargs):
        super().__init__()

        self._samples = samples
        self._last_value = 0
        if not hasattr(self, '_value'):
            self._value = None

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
    def value(self):
        return self._value

    @staticmethod
    def load_config(pi_timer, config):

        sensors = {}
        for sensor, config in config.items():
            def create_dhtxx_sensor(variant):
                return variant(channel=config.get('channel'),
                               value_index=i,
                               power_channel=config.get('power_channel'),
                               pi_timer=pi_timer)

            type_ = config.get('type', '').replace('-', '_').upper()

            if type_ in DHT11Input.provides or type_ in DHT22Input.provides:
                if type_ in DHT11Input.provides:
                    dht_variant = DHT11Input
                else:
                    dht_variant = DHT22Input
                for i, val in enumerate(config.get('provides')):
                    sensors['{}.{}'.format(sensor, val)] = create_dhtxx_sensor(dht_variant)

            elif type_ in OneWireInput.provides:
                sensors[sensor] = OneWireInput(**config)

            elif type_ in UltrasonicInput.provides:
                sensors[sensor] = UltrasonicInput(pi_timer=pi_timer, **config)

            elif type_ in HomeLabPH.provides:
                sensors['{}.pH'.format(sensor)] = HomeLabPH(value_index='pH')
                sensors['{}.temperature'.format(sensor)] = HomeLabPH(value_index='t')
        return sensors

    def _main_loop(self):
        while self._continue:
            vals = []
            for i in range(self._samples):
                v = self._read()
                if v:
                    vals.append(self.value_processor(v))
            if vals:
                self._value = avg(vals)
            time.sleep(self.frequency)

    def _read(self):
        raise NotImplementedError

    def to_json(self):
        return 'foo'


from py_hydropi.lib.modules.sensors.dhtxx import DHT11Input, DHT22Input
from py_hydropi.lib.modules.sensors.one_wire import OneWireInput
from py_hydropi.lib.modules.sensors.hc_sr04 import UltrasonicInput
from py_hydropi.lib.modules.sensors.homelab_ph import HomeLabPH
