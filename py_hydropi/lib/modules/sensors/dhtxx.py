import os
import time

if os.environ.get('PY_HYDROPI_TESTING', '').lower() == 'true':
    class Adafruit_DHT:
        value = 10, 10

        @classmethod
        def read_retry(cls, _, channel):
            return cls.value
else:
    import Adafruit_DHT

from py_hydropi.lib.modules.inputs import Input


class DHTxxInput(Input):
    sensor_type = None

    def __init__(self, channel=None, value_index=None, power_channel=None, pi_timer=None, **kwargs):
        super().__init__(**kwargs)
        if power_channel is not None and value_index == 0:
            assert pi_timer is not None
            self.gpio = pi_timer.gpio
            self.power_channel = int(power_channel)
            self.gpio.setup_output_channel(self.power_channel)
            self.gpio.set_output_on(self.power_channel)

        assert channel and value_index is not None
        self.channel = channel
        self.value_index = value_index

    def _read(self):
        val = None
        try:
            val = Adafruit_DHT.read_retry(self.sensor_type, self.channel)
            val = val[self.value_index]
        except IndexError:
            self.logger.error('error processing response from sensor channel {}({})'.format(
                self.channel, self.value_index))
        except Exception as e:
            self.logger.error('{} error reading from {}: channel {}({})'.format(
                e, self.__class__.__name__, self.channel, self.value_index))
        if val is None:
            self.logger.error('{}: {}({}) returned None'.format(
                self.__class__.__name__, self.channel, self.value_index))
        self.power_cycle()
        return val

    def power_cycle(self):
        if hasattr(self, 'power_channel'):
            self.gpio.set_output_off(self.power_channel)
            time.sleep(1)
            self.gpio.set_output_on(self.power_channel)


class DHT11Input(DHTxxInput):
    provides = ('DHT11', 'DHT-11')
    sensor_type = 11
    frequency = 10


class DHT22Input(DHTxxInput):
    provides = ('DHT22', 'DHT-22')
    sensor_type = 22
    frequency = 10
