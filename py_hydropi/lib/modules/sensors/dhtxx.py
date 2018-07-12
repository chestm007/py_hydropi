import os

if os.environ.get('PY_HYDROPI_TESTING') == 'true':
    class Adafruit_DHT:
        @staticmethod
        def read_retry(_, channel):
            return 10, 10
else:
    import Adafruit_DHT

from py_hydropi.lib.modules.inputs import Input


class DHTxxInput(Input):
    sensor_type = None

    def __init__(self, channel=None, value_index=None, **kwargs):
        super().__init__(**kwargs)
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
        except Exception:
            self.logger.error('error reading from {}: channel {}({})'.format(
                self.__class__.__name__, self.channel, self.value_index))
        return val


class DHT11Input(DHTxxInput):
    provides = ('DHT11', )
    sensor_type = 11


class DHT22Input(DHTxxInput):
    provides = ('DHT22', )
    sensor_type = 22